import React from 'react';
import { Box, Button, Paper } from '@mui/material';
import EndpointSelector from './EndpointSelector';
import DateRangeSelector from './DateRangeSelector';
import SearchBox from './SearchBox';
import DataLoadingProgress from './DataLoadingProgress';
import CategorizedCounts from './CategorizedCounts';
import CategoryDetails from './CategoryDetails';

const Sidebar = ({
  selectedEndpoint,
  onEndpointChange,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onSearch,
  onGetData,
  onExport,
  onCategorize,
  onLoadFavorites,
  onClear,
  showCategories,
  onCloseCategorization,
  categorizedData,
  onCategoryClick,
  selectedCategory,
  onBackToCategories,
  categoryItems,
  onFavorite,
  onRowClick,
  selectedRows,
  isLoading,
  loadingProgress,
  loadingStatus
}) => {
  const isGetDataDisabled = !selectedEndpoint || !startDate || !endDate;

  return (
    <Paper elevation={3} sx={{ width: 300, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2 }}>
        <EndpointSelector selectedEndpoint={selectedEndpoint} onEndpointChange={onEndpointChange} />
        <DateRangeSelector startDate={startDate} endDate={endDate} onStartDateChange={onStartDateChange} onEndDateChange={onEndDateChange} />
        <SearchBox onSearch={onSearch} />
        <Button variant="contained" onClick={onGetData} disabled={isGetDataDisabled} fullWidth sx={{ mt: 1 }}>Get Data</Button>
        <Button variant="contained" onClick={onExport} fullWidth sx={{ mt: 1 }}>Export</Button>
        <Button variant="contained" onClick={onCategorize} fullWidth sx={{ mt: 1 }}>Categorize</Button>
        <Button variant="contained" onClick={onLoadFavorites} fullWidth sx={{ mt: 1 }}>Favorites</Button>
        <Button variant="contained" onClick={onClear} fullWidth sx={{ mt: 1 }}>Clear</Button>
        {showCategories && <Button variant="contained" onClick={onCloseCategorization} fullWidth sx={{ mt: 1 }}>Close Categories</Button>}
      </Box>
      <DataLoadingProgress isLoading={isLoading} progress={loadingProgress} status={loadingStatus} />
      {showCategories && (
        <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
          {selectedCategory ? (
            <>
              <Button variant="outlined" onClick={onBackToCategories} sx={{ mb: 2 }}>Back to Categories</Button>
              <CategoryDetails category={selectedCategory} items={categoryItems} onFavorite={onFavorite} onRowClick={onRowClick} selectedRows={selectedRows} />
            </>
          ) : (
            <CategorizedCounts categorizedData={categorizedData} onCategoryClick={onCategoryClick} />
          )}
        </Box>
      )}
    </Paper>
  );
};

export default Sidebar;
