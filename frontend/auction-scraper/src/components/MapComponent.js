import React, { useRef, useEffect, useState, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import ClusterSidebar from './ClusterSidebar';
import { iconConfigs, getCategoryFromUrl } from './utils';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'pk.eyJ1IjoibWFwczJtYXB3aXRoIiwiYSI6ImNtMXhkY2ZuZzA1aDcyanB6cTlwcGR4Y2IifQ.aFQgruBVDzb2fmF112BhMw';

const MapComponent = React.memo(({ data, selectedEndpoint, onClusterClick, onRowSelect, selectedRows, handleFavorite, updateTrigger, darkMode, center, zoom }) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [clusterData, setClusterData] = useState([]);

  const initializeMap = useCallback(() => {
    if (mapRef.current) return;

    // Disable telemetry to prevent CORS issues
    mapboxgl.config.SEND_ANONYMOUS_USAGE_STATS = false;

    // Check if center is valid
    const validCenter = Array.isArray(center) && center.length === 2 && 
                        !isNaN(center[0]) && !isNaN(center[1]) ? 
                        center : [-93.2140, 42.0046]; // Default to Iowa if invalid

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: darkMode ? 'mapbox://styles/mapbox/dark-v11' : 'mapbox://styles/mapbox/light-v11',
      center: validCenter,
      zoom: zoom || 6, // Provide a default zoom if not specified
    });

    mapRef.current.on('load', setupMapLayers);
    
    // Add error handling for map load
    mapRef.current.on('error', (e) => {
      console.error('Mapbox GL JS error:', e);
    });

  }, [darkMode, center, zoom]);

  const setupMapLayers = useCallback(() => {
    const map = mapRef.current;
    if (!map.getSource('auctions')) {
      map.addSource('auctions', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 30
      });

      // Cluster layer
      map.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'auctions',
        filter: ['has', 'point_count'],
        paint: {
          'circle-color': [
            'step',
            ['get', 'point_count'],
            '#51bbd6',
            10,
            '#f1f075',
            50,
            '#f28cb1'
          ],
          'circle-radius': [
            'step',
            ['get', 'point_count'],
            20,
            10,
            30,
            50,
            40
          ]
        }
      });

      // Cluster count layer
      map.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'auctions',
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
          'text-size': 12
        }
      });

      // Unclustered point layer
      map.addLayer({
        id: 'unclustered-point',
        type: 'circle',
        source: 'auctions',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': '#11b4da',
          'circle-radius': 10,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#fff'
        }
      });
    }

    // Event listeners
    map.on('click', 'clusters', (e) => {
      const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
      const clusterId = features[0].properties.cluster_id;
      const pointCount = features[0].properties.point_count;
      const clusterSource = map.getSource('auctions');

      clusterSource.getClusterLeaves(clusterId, pointCount, 0, (err, aFeatures) => {
        if (err) {
          console.error('Error getting cluster leaves:', err);
          return;
        }
        
        const clusterItems = aFeatures.map(f => f.properties);
        setClusterData(clusterItems);
        setSidebarVisible(true);
      });
    });

    map.on('click', 'unclustered-point', (e) => {
      const properties = e.features[0].properties;
      setClusterData([properties]);
      setSidebarVisible(true);
    });
  }, []);

  const handleClusterClick = useCallback((e) => {
    const features = mapRef.current.queryRenderedFeatures(e.point, { layers: ['clusters'] });
    const clusterId = features[0].properties.cluster_id;
    const pointCount = features[0].properties.point_count;
    const clusterSource = mapRef.current.getSource('auctions');

    clusterSource.getClusterLeaves(clusterId, pointCount, 0, (err, aFeatures) => {
      if (err) {
        console.error('Error getting cluster leaves:', err);
        return;
      }
      
      const clusterItems = aFeatures.map(f => f.properties);
      setClusterData(clusterItems);
      setSidebarVisible(true);
    });
  }, []);

  const handleUnclusteredPointClick = useCallback((e) => {
    const properties = e.features[0].properties;
    setClusterData([properties]);
    setSidebarVisible(true);
  }, []);

  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.on('click', 'clusters', handleClusterClick);
      mapRef.current.on('click', 'unclustered-point', handleUnclusteredPointClick);
    }
    return () => {
      if (mapRef.current) {
        mapRef.current.off('click', 'clusters', handleClusterClick);
        mapRef.current.off('click', 'unclustered-point', handleUnclusteredPointClick);
      }
    };
  }, [handleClusterClick, handleUnclusteredPointClick]);

  const updateMapData = useCallback(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return;

    const features = data
      .filter(item => !isNaN(parseFloat(item.longitude)) && !isNaN(parseFloat(item.latitude)))
      .map(item => ({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [parseFloat(item.longitude), parseFloat(item.latitude)]
        },
        properties: {
          ...item,
          category: item.url ? getCategoryFromUrl(item.url) : 'default'
        }
      }));

    const source = mapRef.current.getSource('auctions');
    if (source) {
      source.setData({
        type: 'FeatureCollection',
        features: features
      });
    }
  }, [data]);

  useEffect(() => {
    initializeMap();
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [initializeMap]);

  useEffect(() => {
    if (mapRef.current && mapRef.current.isStyleLoaded()) {
      updateMapData();
    } else {
      mapRef.current?.once('style.load', updateMapData);
    }
  }, [updateMapData, updateTrigger]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', display: 'flex' }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />
      {sidebarVisible && (
        <ClusterSidebar
          data={clusterData}
          onClose={() => setSidebarVisible(false)}
          onFavorite={handleFavorite}
          onRowClick={onRowSelect}
          selectedRows={selectedRows}
          darkMode={darkMode}
        />
      )}
    </div>
  );
});

export default MapComponent;
