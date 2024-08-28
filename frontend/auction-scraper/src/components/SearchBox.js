import React, { useState } from 'react';

function SearchBox({ onSearch }) {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    if (onSearch) {
      onSearch(query);
    }
  };

  return (
    <div className="search-box">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search auctions..."
      />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}

export default SearchBox;
