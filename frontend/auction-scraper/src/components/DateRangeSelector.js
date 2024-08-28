import React from 'react';

const DateRangeSelector = ({ startDate, endDate, onStartDateChange, onEndDateChange }) => {
  return (
    <div>
      <input
        type="date"
        value={startDate}
        onChange={(e) => onStartDateChange(e.target.value)}
      />
      <input
        type="date"
        value={endDate}
        onChange={(e) => onEndDateChange(e.target.value)}
      />
    </div>
  );
};

export default DateRangeSelector;