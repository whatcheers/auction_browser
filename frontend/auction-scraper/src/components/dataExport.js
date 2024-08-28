export const exportCSV = (data, filename) => {
  console.debug('Exporting data to CSV:', data);

  if (!data || data.length === 0) {
    console.error('No data available for export');
    return;
  }

  // Extract headers based on the keys of the first object in the data array
  const headers = Object.keys(data[0]);

  // Map the data to CSV rows, joining values by commas
  const csvContent = [
    headers.join(','), // CSV header row
    ...data.map(row => headers.map(fieldName => JSON.stringify(row[fieldName] || '')).join(',')) // CSV rows
  ].join('\n');

  // Create a CSV file and trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  console.debug('CSV export completed');
};
