import React from 'react';

export default function Filters({ filters, setFilters }) {
  return (
    <div className="filters">
      <h3>Filters</h3>
      <label>
        Participant
        <input
          type="text"
          placeholder="e.g. Alice"
          value={filters.participant}
          onChange={(e) => setFilters({ ...filters, participant: e.target.value })}
        />
      </label>
      <label>
        Start Date
        <input
          type="date"
          value={filters.startDate}
          onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
        />
      </label>
      <label>
        End Date
        <input
          type="date"
          value={filters.endDate}
          onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
        />
      </label>
    </div>
  );
}
