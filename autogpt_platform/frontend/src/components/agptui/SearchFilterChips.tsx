"use client";

import * as React from "react";

interface FilterOption {
  label: string;
  count: number;
  value: string;
}

interface SearchFilterChipsProps {
  totalCount?: number;
  agentsCount?: number;
  creatorsCount?: number;
}

export const SearchFilterChips: React.FC<SearchFilterChipsProps> = ({
  totalCount = 10,
  agentsCount = 8,
  creatorsCount = 2,
}) => {
  const [selected, setSelected] = React.useState("all");

  const filters: FilterOption[] = [
    { label: "All", count: totalCount, value: "all" },
    { label: "Agents", count: agentsCount, value: "agents" },
    { label: "Creators", count: creatorsCount, value: "creators" },
  ];

  const handleFilterClick = (value: string) => {
    setSelected(value);
    console.log(`Filter selected: ${value}`);
  };

  return (
    <div className="flex gap-2.5">
      {filters.map((filter) => (
        <button
          key={filter.value}
          onClick={() => handleFilterClick(filter.value)}
          className={`px-5 py-2 rounded-[34px] flex items-center gap-2.5 ${
            selected === filter.value
              ? "bg-neutral-800 text-white"
              : "border border-neutral-600 text-neutral-800"
          }`}
        >
          <span className={`text-base ${selected === filter.value ? "font-medium" : ""}`}>
            {filter.label}
          </span>
          <span className={`text-base ${selected === filter.value ? "font-medium" : ""}`}>
            {filter.count}
          </span>
        </button>
      ))}
    </div>
  );
};