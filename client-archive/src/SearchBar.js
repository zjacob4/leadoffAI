"use client";
import * as React from "react";

export function SearchBar({ searchQuery, onSearch, onSearchSubmit }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearchSubmit(searchQuery);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="relative mx-auto my-0 max-w-[600px] flex"
    >
      <input
        className="px-6 py-4 w-full text-lg rounded-l-xl border-2 border-solid border-r-0 shadow-md transition-all border-slate-200 duration-[0.3s] ease-[ease]"
        type="search"
        placeholder="Search for a player..."
        value={searchQuery}
        onInput={onSearch}
        aria-label="Search for a player"
      />
      <button
        type="submit"
        className="px-6 py-4 bg-indigo-600 text-white font-medium rounded-r-xl hover:bg-indigo-700 transition-colors duration-300 shadow-md"
        aria-label="Search"
      >
        Search
      </button>
    </form>
  );
}
