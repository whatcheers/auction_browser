import React, { useState, useCallback, useRef, useEffect } from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Container, 
  Paper, 
  Switch,
  CssBaseline,
  FormControlLabel,
  Snackbar,
  Alert
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import MapComponent from './components/MapComponent';
import EndpointSelector from './components/EndpointSelector';
import DateRangeSelector from './components/DateRangeSelector';
import { exportCSV } from './components/dataExport';
import { tableNames, getCategoryFromUrl } from './components/utils';
import { categorizeItems as categorizationFunction } from './components/categorizeItems';
import CategorizedCounts from './components/CategorizedCounts';
import CategoryDetails from './components/CategoryDetails';
import LastRunStatus from './components/LastRunStatus';
import SearchBox from './components/SearchBox';
import DataLoadingProgress from './components/DataLoadingProgress';

const apiUrl = process.env.REACT_APP_API_URL || 'https://hashbrowns:3002';

const App = () => {
  const currentDate = new Date().toISOString().split('T')[0];
  const rawDataRef = useRef([]);
  const [categorizedData, setCategorizedData] = useState({});
  const [selectedEndpoint, setSelectedEndpoint] = useState('');
  const [selectedRows, setSelectedRows] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showCategories, setShowCategories] = useState(false);
  const [updateTrigger, setUpdateTrigger] = useState(0);
  const [startDate, setStartDate] = useState(currentDate);
  const [endDate, setEndDate] = useState(currentDate);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [mapData, setMapData] = useState([]);

  const lightTheme = createTheme({
    palette: {
      mode: 'light',
      primary: {
        main: '#3f51b5',
      },
      secondary: {
        main: '#f50057',
      },
    },
  });

  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#90caf9',
      },
      secondary: {
        main: '#f48fb1',
      },
    },
  });

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  // Moved all useCallback hooks to the top level of the component to avoid rule violations.
  // These hooks were previously within other functions, violating the rule of hooks.
  
  const categorizeItems = useCallback((data) => {
    if (data.length === 0) return;

    const categorizedResults = categorizationFunction(data);
    const formattedResults = {};
    categorizedResults.forEach(item => {
      if (!formattedResults[item.category]) {
        formattedResults[item.category] = [];
      }
      formattedResults[item.category].push(item);
    });

    setCategorizedData(formattedResults);
  }, []);

  const handleClusterClick = useCallback((clusterItems) => {
    console.log('Cluster clicked, items:', clusterItems);
  }, []);

  const handleCategorizeClick = useCallback(() => {
    categorizeItems(rawDataRef.current);
    setShowCategories(true);
  }, [categorizeItems]);

  const handleCloseCategorization = useCallback(() => {
    setShowCategories(false);
    setSelectedCategory(null);
  }, []);

  const handleCategoryClick = useCallback((category) => {
    setSelectedCategory(category);
  }, []);

  const handleBackToCategories = useCallback(() => {
    setSelectedCategory(null);
  }, []);

  const handleRowSelect = useCallback((rowUrl) => {
    setSelectedRows((prevSelectedRows) => {
      if (prevSelectedRows.includes(rowUrl)) {
        return prevSelectedRows.filter((url) => url !== rowUrl);
      } else {
        return [...prevSelectedRows, rowUrl];
      }
    });
  }, []);

  const loadAuctionData = useCallback(async () => {
    console.log('loadAuctionData called with:', { selectedEndpoint, startDate, endDate });
    setIsLoading(true);
    setLoadingProgress(0);
    setLoadingStatus('Initializing data load...');
  
    try {
      let url;
      if (selectedEndpoint === 'all_tables') {
        url = `${apiUrl}/api/get-auction-data?tableName=all_tables&startDate=${startDate}&endDate=${endDate}`;
      } else if (selectedEndpoint.includes('php')) {
        url = `https://hashbrowns/bin/get_auction_data.php`;
      } else {
        url = `${apiUrl}/api/get-auction-data?tableName=${selectedEndpoint}&startDate=${startDate}&endDate=${endDate}`;
      }
  
      console.log('Fetching data from URL:', url);
  
      setLoadingStatus('Sending request to server...');
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      setLoadingStatus('Receiving data from server...');
      
      const jsonData = await response.json();
  
      console.log('Data loaded:', jsonData);
      if (Array.isArray(jsonData)) {
        rawDataRef.current = jsonData;
        setMapData(jsonData);  // Ensure mapData is updated
        setError(null);
      } else if (jsonData.error) {
        throw new Error(jsonData.error);
      } else {
        throw new Error('Unexpected data format received from server');
      }
  
      setLoadingStatus('Processing received data...');
      setUpdateTrigger((prev) => prev + 1);
      setLoadingStatus('Data load complete');
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError(error.message);
      setLoadingStatus('Error: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  }, [selectedEndpoint, startDate, endDate]);

  const loadDefaultData = useCallback(() => {
    if (selectedEndpoint === 'ending_today') {
      loadAuctionData();
    } else {
      const startDate = '2024-01-01';
      const endDate = '2024-12-31';
      const url = `${apiUrl}/api/get-auction-data?tableName=${selectedEndpoint}&startDate=${startDate}&endDate=${endDate}`;
  
      fetch(url)
        .then(response => response.json())
        .then(data => {
          rawDataRef.current = data;
          setUpdateTrigger(prev => prev + 1);
        })
        .catch(error => {
          console.error('Failed to fetch default data:', error);
          setError(error.message);
        });
    }
  }, [selectedEndpoint, loadAuctionData]);

  const handleExportClick = useCallback(() => {
    exportCSV(rawDataRef.current, 'selected_data.csv');
  }, []);

  const handleFavorite = useCallback(async (item) => {
    console.log('Toggling favorite status for item:', item);
    const newFavoriteStatus = item.favorite === 'Y' ? 'N' : 'Y';

    let tableName = item.original_table || item.table_name;
    if (!tableName) {
      const category = getCategoryFromUrl(item.url);
      tableName = tableNames[category] || category;
    }

    if (tableName === 'wiscosurp') {
      tableName = 'wiscosurp_auctions';
    }

    console.log('Using table name:', tableName);

    if (!tableName || !item.url) {
      console.error('Missing table name or URL');
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/favorite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          favorite: newFavoriteStatus,
          tableName: tableName,
          lot_number: item.lot_number || '',
          id: item.id || '',
          url: item.url,
        }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error || `HTTP error! status: ${response.status}`);
      }

      if (result.success) {
        console.log('Favorite status updated successfully');
        rawDataRef.current = rawDataRef.current.map(d =>
          d.url === item.url ? { ...d, favorite: newFavoriteStatus } : d
        );
        setUpdateTrigger(prev => prev + 1);
      } else {
        throw new Error(result.error || 'Failed to update favorite status');
      }
    } catch (error) {
      console.error('Error updating favorite status:', error);
      setError('Failed to update favorite status: ' + error.message);
    }
  }, []);

  const handleSearch = useCallback(async (searchQuery) => {
    console.log('handleSearch called with query:', searchQuery);
  
    if (!selectedEndpoint) {
      setError('Please select an endpoint before searching.');
      return;
    }
  
    if (searchQuery.trim() === '') {
      loadDefaultData();
      return;
    }
  
    try {
      let url;
  
      const params = new URLSearchParams();
      params.append('searchTerm', encodeURIComponent(searchQuery));
      params.append('startDate', startDate);
      params.append('endDate', endDate);
  
      if (selectedEndpoint === 'all_tables') {
        url = `${apiUrl}/api/search-auction-data?tableName=all_tables&${params.toString()}`;
      } else if (selectedEndpoint === 'ending_today') {
        url = `https://hashbrowns/bin/get_auction_data.php?todayOnly=true&${params.toString()}`;
      } else {
        url = `${apiUrl}/api/search-auction-data?tableName=${selectedEndpoint}&${params.toString()}`;
      }
  
      console.log('Fetching search results from URL:', url);
  
      const response = await fetch(url);
      const result = await response.json();
  
      if (response.ok) {
        console.log('Search results loaded:', result);
        rawDataRef.current = result;
        setMapData(result);  // Update mapData with the search results
        setError(null);
        setUpdateTrigger((prev) => prev + 1);
      } else {
        if (response.status === 404 && result.error) {
          setError(result.error);
          rawDataRef.current = [];
          setMapData([]);  // Clear mapData if no results found
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
    } catch (error) {
      console.error('Failed to fetch search results:', error);
      setError(error.message);
    }
  }, [selectedEndpoint, startDate, endDate, loadDefaultData]);

  const loadFavoritesData = useCallback(async () => {
    console.log('Loading favorites data');
    setIsLoading(true);
    setLoadingStatus('Loading favorites...');
    try {
      const response = await fetch(`${apiUrl}/api/favorites`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const favoritesData = await response.json();
      console.log('Favorites data loaded:', favoritesData);
      rawDataRef.current = favoritesData;
      setMapData(favoritesData);
      categorizeItems(favoritesData);
      setUpdateTrigger(prev => prev + 1);
      setLoadingStatus('Favorites loaded successfully');
    } catch (err) {
      console.error('Failed to fetch favorites data:', err.message);
      setError('Failed to load favorites: ' + err.message);
      setLoadingStatus('Error loading favorites');
    } finally {
      setIsLoading(false);
    }
    
  }, [apiUrl, categorizeItems]);

  useEffect(() => {
    console.log('Current state:', { selectedEndpoint, startDate, endDate });
  }, [selectedEndpoint, startDate, endDate]);

  const isGetDataDisabled = !selectedEndpoint || !startDate || !endDate;

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Auction Data Viewer
            </Typography>
            <LastRunStatus apiUrl={apiUrl} />
            <FormControlLabel
              control={
                <Switch
                  checked={darkMode}
                  onChange={toggleDarkMode}
                  icon={<Brightness7Icon />}
                  checkedIcon={<Brightness4Icon />}
                />
              }
              label={darkMode ? "Dark Mode" : "Light Mode"}
            />
          </Toolbar>
        </AppBar>
        <Container maxWidth={false} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            alignItems: 'center', 
            gap: 1, 
            mb: 2,
            '& > *': { minWidth: 'auto', flexShrink: 0 }
          }}>
            <EndpointSelector
              selectedEndpoint={selectedEndpoint}
              onEndpointChange={setSelectedEndpoint}
            />
            <DateRangeSelector
              startDate={startDate}
              endDate={endDate}
              onStartDateChange={setStartDate}
              onEndDateChange={setEndDate}
            />
            <Button 
              variant="contained" 
              onClick={loadAuctionData} 
              disabled={isGetDataDisabled}
              size="small"
            >
              Get Data
            </Button>
            <Button variant="contained" onClick={handleExportClick} size="small">Export</Button>
            <Button variant="contained" onClick={handleCategorizeClick} size="small">Categorize</Button>
            <Button variant="contained" onClick={loadFavoritesData} size="small">Favorites</Button>
            {showCategories && (
              <Button variant="contained" onClick={handleCloseCategorization} size="small">Close Categories</Button>
            )}
            <Button variant="contained" onClick={loadDefaultData} size="small">Clear</Button>
            <Box sx={{ flexGrow: 1, minWidth: '200px' }}>
              <SearchBox onSearch={handleSearch} />
            </Box>
          </Box>
          <DataLoadingProgress 
            isLoading={isLoading}
            progress={loadingProgress}
            status={loadingStatus}
          />
          <Box sx={{ flexGrow: 1, display: 'flex', minHeight: 0 }}>
            <Paper 
              elevation={3} 
              sx={{ 
                flexGrow: 1, 
                display: 'flex', 
                flexDirection: 'column',
                overflow: 'hidden',
                mr: showCategories ? 2 : 0
              }}
            >
              <MapComponent
                data={mapData}  // Pass the updated mapData
                selectedEndpoint={selectedEndpoint}
                onClusterClick={handleClusterClick}
                onRowSelect={handleRowSelect}
                selectedRows={selectedRows}
                handleFavorite={handleFavorite}
                updateTrigger={updateTrigger}
                darkMode={darkMode}  // Pass darkMode to MapComponent
              />
            </Paper>
            {showCategories && (
              <Paper 
                elevation={3} 
                sx={{ 
                  width: 300, 
                  p: 2, 
                  overflowY: 'auto', 
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                {selectedCategory ? (
                  <>
                    <Button variant="outlined" onClick={handleBackToCategories} sx={{ mb: 2 }}>
                      Back to Categories
                    </Button>
                    <CategoryDetails
                      category={selectedCategory}
                      items={categorizedData[selectedCategory]}
                      onFavorite={handleFavorite}
                      onRowClick={handleRowSelect}
                      selectedRows={selectedRows}
                    />
                  </>
                ) : (
                  <CategorizedCounts
                    categorizedData={categorizedData}
                    onCategoryClick={handleCategoryClick}
                  />
                )}
              </Paper>
            )}
          </Box>
        </Container>
      </Box>
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;