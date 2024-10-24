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
  CssBaseline,
  Snackbar,
  Alert,
  IconButton
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import MapComponent from './components/MapComponent';
import EndpointSelector from './components/EndpointSelector';
import DateRangeSelector from './components/DateRangeSelector';
import { exportCSV } from './components/dataExport';
import { tableNames, getCategoryFromUrl } from './components/utils';
import { categorizeItems } from './components/categorizeItems';
import CategorizedCounts from './components/CategorizedCounts';
import CategoryDetails from './components/CategoryDetails';
import DailyAverages from './components/DailyAverages';
import SearchBox from './components/SearchBox';
import DataLoadingProgress from './components/DataLoadingProgress';
import AlertManager from './components/AlertManager';
import CategorySidebar from './components/CategorySidebar';
import PopupContent from './components/PopupContent';
import Link from '@mui/material/Link';
import debounce from 'lodash/debounce';

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
  const isLoadingRef = useRef(false);
  const [popupContent, setPopupContent] = useState(null);
  const [popupState, setPopupState] = useState({ position: { x: 0, y: 0 }, size: { width: 0, height: 0 } });

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

  const handleCategorization = useCallback((data) => {
    if (!Array.isArray(data) || data.length === 0) {
      console.log("No data to categorize in handleCategorization");
      return {};
    }

    const categorizedResults = categorizeItems(data);
    const formattedResults = {};
    
    categorizedResults.forEach(item => {
      if (!formattedResults[item.category]) {
        formattedResults[item.category] = [];
      }
      formattedResults[item.category].push(item);
    });
    
    console.log("Formatted results in handleCategorization:", formattedResults);
    return formattedResults;
  }, []);

  const handleClusterClick = useCallback((clusterItems) => {
    console.log('Cluster clicked, items:', clusterItems);
  }, []);

  const handleCategorizeClick = useCallback(() => {
    if (rawDataRef.current.length === 0) {
      console.log("No data to categorize");
      return;
    }
    
    console.log("Raw data:", rawDataRef.current); // Log raw data
    
    const categorizedResults = handleCategorization(rawDataRef.current);
    
    console.log("Categorized results:", categorizedResults); // Log categorized results
    
    if (!categorizedResults || typeof categorizedResults !== 'object') {
      console.error("Categorization failed: invalid result", categorizedResults);
      return;
    }
    
    const categoryCounts = Object.entries(categorizedResults).map(([category, items]) => ({ 
      category, 
      itemCount: Array.isArray(items) ? items.length : 0 
    }));
    
    console.log("Category counts:", categoryCounts); // Log category counts

    setPopupContent({
      features: categoryCounts,
      type: 'categories'
    });
    setPopupState({ position: { x: 100, y: 100 }, size: { width: 300, height: 400 } });
  }, [handleCategorization]);

  const handleCloseCategorization = useCallback(() => {
    setShowCategories(false);
    setSelectedCategory(null);
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
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;
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
      
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
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
      isLoadingRef.current = false;
    }
  }, [selectedEndpoint, startDate, endDate]);

  const loadAuctionDataRef = useRef(loadAuctionData);
  
  useEffect(() => {
    loadAuctionDataRef.current = loadAuctionData;
  }, [loadAuctionData]);

  const debouncedLoadAuctionData = useCallback(() => {
    const debouncedFunction = debounce(() => {
      loadAuctionData();
    }, 300);
    
    debouncedFunction();
    
    // Cleanup function to cancel the debounce if the component unmounts or the callback changes
    return () => debouncedFunction.cancel();
  }, [loadAuctionData]);

  const loadDefaultData = useCallback(() => {
    if (selectedEndpoint === 'ending_today') {
      debouncedLoadAuctionData();
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
  }, [selectedEndpoint, debouncedLoadAuctionData]);

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

    setIsLoading(true);
    setError(null);

    try {
      const currentDate = new Date();
      const startDate = currentDate.toISOString().split('T')[0];
      const endDate = new Date(currentDate.setDate(currentDate.getDate() + 90)).toISOString().split('T')[0];

      const params = new URLSearchParams({
        tableName: selectedEndpoint,
        startDate: startDate,
        endDate: endDate,
        searchTerm: searchQuery
      });

      const url = `${apiUrl}/api/get-auction-data?${params.toString()}`;

      console.log('Fetching search results from URL:', url);

      const response = await fetch(url);

      if (response.status === 404) {
        console.log(`No items found for "${searchQuery}" in the next 90 days.`);
        rawDataRef.current = [];
        setMapData([]);
        setError(`No items found for "${searchQuery}" in the next 90 days.`);
      } else if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      } else {
        const result = await response.json();
        console.log('Search results loaded:', result);
        rawDataRef.current = result;
        setMapData(result);
      }
      setUpdateTrigger((prev) => prev + 1);
    } catch (error) {
      console.error('Failed to fetch search results:', error);
      setError(`Error: ${error.message}`);
      rawDataRef.current = [];
      setMapData([]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedEndpoint]); // Removed apiUrl from the dependency array

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
      handleCategorization(favoritesData);
      setUpdateTrigger(prev => prev + 1);
      setLoadingStatus('Favorites loaded successfully');
    } catch (err) {
      console.error('Failed to fetch favorites data:', err.message);
      setError('Failed to load favorites: ' + err.message);
      setLoadingStatus('Error loading favorites');
    } finally {
      setIsLoading(false);
    }
    
  }, [handleCategorization]); // Removed apiUrl from the dependency array
  useEffect(() => {
    console.log('Current state:', { selectedEndpoint, startDate, endDate });
  }, [selectedEndpoint, startDate, endDate]);

  const isGetDataDisabled = !selectedEndpoint || !startDate || !endDate;

  const handleCloseCategorySidebar = useCallback(() => {
    setShowCategories(false);
  }, []);

  const handleCategoryClick = useCallback((category) => {
    const categorizedItems = categorizeItems(rawDataRef.current).filter(item => item.category === category);
    setPopupContent({
      features: categorizedItems,
      type: 'items'
    });
  }, []);

  const handleAlertClick = useCallback(async (data, keyword) => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('Alert data loaded:', data);
      if (Array.isArray(data) && data.length > 0) {
        rawDataRef.current = data;
        setMapData(data);
        setUpdateTrigger(prev => prev + 1);
        const categorizedResults = handleCategorization(data);
        setCategorizedData(categorizedResults);
      } else {
        console.log(`No items found for "${keyword}" in the next 90 days.`);
        rawDataRef.current = [];
        setMapData([]);
        setCategorizedData({});
        setError(`No items found for "${keyword}" in the next 90 days.`);
      }
    } catch (err) {
      console.error('Error processing alert data:', err);
      setError(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [handleCategorization]);

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Auction Data Viewer
            </Typography>
            <Link
              href="http://hashbrowns:3001/"
              target="_blank"
              rel="noopener noreferrer"
              color="inherit"
              sx={{ mr: 2, textDecoration: 'none' }}
            >
              Auction Research
            </Link>
            <DailyAverages apiUrl={apiUrl} />
            <AlertManager onAlertClick={handleAlertClick} />
            <IconButton onClick={toggleDarkMode} color="inherit">
              {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Toolbar>
        </AppBar>
        <Container maxWidth={false} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 1, mb: 2, '& > *': { minWidth: 'auto', flexShrink: 0 } }}>
            <EndpointSelector selectedEndpoint={selectedEndpoint} onEndpointChange={setSelectedEndpoint} />
            <DateRangeSelector startDate={startDate} endDate={endDate} onStartDateChange={setStartDate} onEndDateChange={setEndDate} />
            <Button variant="contained" onClick={debouncedLoadAuctionData} disabled={isGetDataDisabled} size="small">Get Data</Button>
            <Button variant="contained" onClick={handleExportClick} size="small">Export</Button>
            <Button variant="contained" onClick={handleCategorizeClick} size="small">Categorize</Button>
            <Button variant="contained" onClick={loadFavoritesData} size="small">Favorites</Button>
            {showCategories && <Button variant="contained" onClick={handleCloseCategorization} size="small">Close Categories</Button>}
            <Button variant="contained" onClick={loadDefaultData} size="small">Clear</Button>
            <Box sx={{ flexGrow: 1, minWidth: '200px' }}>
              <SearchBox onSearch={handleSearch} />
            </Box>
          </Box>
          <DataLoadingProgress isLoading={isLoading} progress={loadingProgress} status={loadingStatus} />
          <Box sx={{ flexGrow: 1, display: 'flex', minHeight: 0 }}>
            <Paper elevation={3} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', mr: showCategories ? 2 : 0 }}>
              <MapComponent 
                data={mapData.filter(item => item.latitude && item.longitude)} 
                selectedEndpoint={selectedEndpoint} 
                onClusterClick={handleClusterClick} 
                onRowSelect={handleRowSelect} 
                selectedRows={selectedRows} 
                handleFavorite={handleFavorite} 
                updateTrigger={updateTrigger} 
                darkMode={darkMode} 
              />
            </Paper>
            {showCategories && (
              <Paper elevation={3} sx={{ width: 300, p: 2, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                {selectedCategory ? (
                  <>
                    <Button variant="outlined" onClick={handleBackToCategories} sx={{ mb: 2 }}>Back to Categories</Button>
                    <CategoryDetails category={selectedCategory} items={categorizedData[selectedCategory]} onFavorite={handleFavorite} onRowClick={handleRowSelect} selectedRows={selectedRows} />
                  </>
                ) : (
                  <CategorizedCounts categorizedData={categorizedData} onCategoryClick={handleCategoryClick} />
                )}
              </Paper>
            )}
          </Box>
        </Container>
      </Box>
      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>{error}</Alert>
      </Snackbar>
      {showCategories && (
        <CategorySidebar 
          categorizedData={categorizedData}
          onClose={handleCloseCategorySidebar}
          onCategoryClick={handleCategoryClick}
        />
      )}
      {popupContent && (
        <PopupContent
          features={popupContent.features}
          onClose={() => setPopupContent(null)}
          onFavorite={handleFavorite}
          onRowClick={popupContent.type === 'categories' ? handleCategoryClick : handleRowSelect}
          selectedRows={selectedRows}
          popupState={popupState}
          onPopupChange={setPopupState}
          darkMode={darkMode}
          type={popupContent.type}
        />
      )}
    </ThemeProvider>
  );
}

export default App;
