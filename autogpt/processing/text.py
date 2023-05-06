"""Text processing functions"""
from math import ceil
from typing import Dict, Generator, Optional

import spacy
import tiktoken

from autogpt.config import Config
from autogpt.llm.llm_utils import create_text_completion
from autogpt.llm.providers.openai import OPEN_AI_MODELS
from autogpt.llm.token_counter import count_string_tokens
from autogpt.logs import logger
from autogpt.utils import batch

CFG = Config()


def _max_chunk_length(model: str, max: Optional[int] = None) -> int:
    model_max_input_tokens = OPEN_AI_MODELS[model].max_tokens - 1
    if max is not None and max > 0:
        return min(max, model_max_input_tokens)
    return model_max_input_tokens


def must_chunk_content(
    text: str, for_model: str, max_chunk_length: Optional[int] = None
) -> bool:
    return count_string_tokens(text, for_model) > _max_chunk_length(
        for_model, max_chunk_length
    )


def chunk_content(
    content: str,
    for_model: str,
    max_chunk_length: Optional[int] = None,
    with_overlap=True,
):
    """Split content into chunks of approximately equal token length."""

    MAX_OVERLAP = 200  # limit overlap to save tokens

    if not must_chunk_content(content, for_model, max_chunk_length):
        yield content, count_string_tokens(content, for_model)
        return

    max_chunk_length = max_chunk_length or _max_chunk_length(for_model)

    tokenizer = tiktoken.encoding_for_model(for_model)

    tokenized_text = tokenizer.encode(content)
    total_length = len(tokenized_text)
    n_chunks = ceil(total_length / max_chunk_length)

    chunk_length = ceil(total_length / n_chunks)
    overlap = min(max_chunk_length - chunk_length, MAX_OVERLAP) if with_overlap else 0

    for token_batch in batch(tokenized_text, chunk_length + overlap, overlap):
        yield tokenizer.decode(token_batch), len(token_batch)


def summarize_text(
    text: str, question: Optional[str] = None, max_chunk_length: Optional[int] = None
) -> tuple[str, None | list[tuple[str, str]]]:
    """Summarize text using the OpenAI API

    Args:
        text (str): The text to summarize
        question (str): A question to focus the summary content

    Returns:
        str: The summary of the text
        list[(summary, chunk)]: Text chunks and their summary, if the text was chunked.
            None otherwise.
    """
    if not text:
        raise ValueError("No text to summarize")

    # model = CFG.fast_llm_model      # does not support text completion :(
    model = "text-davinci-003"

    summarization_prompt_template = (
        (
            "Consisely summarize the following text, focusing on "
            f'information related to the question "{question}". '
            "Do not answer the question itself. "
            "If the text does not contain information, describe the type of text.\n"
            '\nText: """{content}"""\n'
            "\nSummary/description:"
        )
        if question is not None
        else (
            "Consisely summarize the following text, "
            "covering the topics present in the text and nothing more. "
            "If the text does not contain information, describe the type of text.\n"
            '\nText: """{content}"""\n'
            "\nSummary/description:"
        )
    )

    token_length = count_string_tokens(text, model)
    logger.info(f"Text length: {token_length} tokens")

    if not must_chunk_content(
        text, model, _max_chunk_length(model, max_chunk_length) - 550
    ):  # reserve 50 tokens for summary prompt, 500 for the response
        prompt = summarization_prompt_template.format(content=text)
        logger.debug(f"Summarizing with {model}:\n{'-'*32}\n{prompt}\n{'-'*32}\n")
        summary = create_text_completion(prompt, model, temperature=0, max_output_tokens=500)
        logger.debug(f"Summary:\n{'-'*32}\n{summary}\n{'-'*32}\n")
        return summary, None

    summaries: list[str] = []
    chunks = list(split_text(text, for_model=model))

    for i, (chunk, chunk_length) in enumerate(chunks):
        logger.info(
            f"Summarizing chunk {i + 1} / {len(chunks)} of length {chunk_length} tokens"
        )
        summary, _ = summarize_text(chunk, question)
        summaries.append(summary)

    logger.info(f"Summarized {len(chunks)} chunks")

    summary, _ = summarize_text("\n\n".join(summaries))

    return summary, [(summaries[i], chunks[i][0]) for i in range(0, len(chunks))]


def split_text(
    text: str,
    for_model: str = CFG.fast_llm_model,
    max_chunk_length: Optional[int] = None,
):
    """Split text into chunks of sentences, with each chunk not exceeding the maximum length

    Args:
        text (str): The text to split
        for_model (str): The model to chunk for; determines tokenizer and constraints
        max_length (int, optional): The maximum length of each chunk

    Yields:
        str: The next chunk of text

    Raises:
        ValueError: when a sentence is longer than the maximum length
    """
    max_length = max_chunk_length or _max_chunk_length(for_model)

    # flatten paragraphs to improve performance
    text = text.replace("\n", " ")
    text_length = count_string_tokens(text, for_model)

    if text_length < max_length:
        yield text, text_length
        return

    n_chunks = ceil(text_length / max_length)
    target_chunk_length = ceil(text_length / n_chunks)

    nlp: spacy.language.Language = spacy.load(CFG.browse_spacy_language_model)
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    sentences = [sentence.text.strip() for sentence in doc.sents]

    current_chunk: list[str] = []
    current_chunk_length = 0

    for sentence in sentences:
        sentence_length = count_string_tokens(sentence, for_model)
        expected_chunk_length = current_chunk_length + 1 + sentence_length

        # TODO: implement overlap
        if (
            expected_chunk_length <= max_length
            # try to create chunks of approximately equal size
            and expected_chunk_length - (sentence_length / 2) < target_chunk_length
        ):
            current_chunk.append(sentence)
            current_chunk_length = expected_chunk_length

        elif sentence_length < max_length:
            yield " ".join(current_chunk), current_chunk_length

            current_chunk = [sentence]
            current_chunk_length = sentence_length

        else:
            raise ValueError(f"Sentence is too long: {sentence_length} tokens.")

    if current_chunk:
        yield " ".join(current_chunk), current_chunk_length
