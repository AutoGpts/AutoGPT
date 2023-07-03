from autogpt.core.resource.schema import (
    ProviderBudget,
    ProviderCredentials,
    ProviderSettings,
    ProviderUsage,
    ResourceType,
)
from autogpt.core.status import ShortStatus, Status

status = Status(
    module_name=__name__,
    short_status=ShortStatus.BASIC_DONE,
    handoff_notes=(
        "Before times: Sketched out BudgetManager.__init__\n"
        "5/6: First interface draft complete.\n"
        "5/7: Basic BudgetManager has been implemented and interface adjustments made.\n"
        "5/10: BudgetManager interface revisions have been PR'ed and merged\n"
        "5/15: Pivot to make resources first class. Add many resource abstractions, port model providers,\n"
        "      port budget manager to resource manager.\n"
        "5/16: The budget system has been radically overhauled to reflect the interconnected nature of budgets,\n"
        "      credentials, and service usage. We're taking a resource-centric approach where, for instance,\n"
        "      we will declare providers of services like language models and then the provider will manage\n"
        "      the budgets, credentials, and any low-level translation for those services. Client classes can then\n"
        "      construct generic models like Memory and LanguageModel and think only about the domain logic and not\n"
        "      the low-level details of how to interact with the service.\n"
    ),
)
