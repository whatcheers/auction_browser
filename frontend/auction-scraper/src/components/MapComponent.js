import React, { useEffect, useRef, useState, useCallback } from 'react';
import 'ol/ol.css';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import { fromLonLat } from 'ol/proj';
import { Vector as VectorLayer } from 'ol/layer';
import { Vector as VectorSource, Cluster } from 'ol/source';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { Style, Icon } from 'ol/style';
import { usePopper } from 'react-popper';
import PopupContent from './PopupContent';
import { getCategoryFromUrl, generateSvgIcon } from './utils';

const MapComponent = React.memo(({ data, selectedEndpoint, onClusterClick, onRowSelect, selectedRows, handleFavorite, updateTrigger }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const vectorSourceRef = useRef(null);
  const vectorLayerRef = useRef(null);
  const popperElementRef = useRef(null);
  const [popupVisible, setPopupVisible] = useState(false);
  const [popupFeatures, setPopupFeatures] = useState([]);
  const [referenceElement, setReferenceElement] = useState(null);
  const [detailedData, setDetailedData] = useState({});

  const { styles, attributes } = usePopper(referenceElement, popperElementRef.current, {
    placement: 'top',
    modifiers: [
      {
        name: 'offset',
        options: {
          offset: [0, 10],
        },
      },
    ],
  });

  const createFeatureStyle = useCallback((feature) => {
    const item = feature.get('itemData');
    return new Style({
      image: new Icon({
        src: generateSvgIcon(getCategoryFromUrl(item.url), undefined, undefined, item.favorite === 'Y'),
        imgSize: [50, 50],
      }),
    });
  }, []);

  const handleFavoriteClick = useCallback((item) => {
    console.log('MapComponent: Toggling favorite status for item:', item);
    handleFavorite(item);
  }, [handleFavorite]);

  const handleRowClick = useCallback((item) => {
    console.log('MapComponent: Row clicked:', item);
    onRowSelect(item.url);
    onClusterClick([item]);
  }, [onRowSelect, onClusterClick]);

  const updateMapFeatures = useCallback(() => {
    if (!vectorSourceRef.current || !Array.isArray(data)) return;

    vectorSourceRef.current.clear();
    data.forEach(item => {
      if (item.latitude && item.longitude) {
        const feature = new Feature({
          geometry: new Point(fromLonLat([parseFloat(item.longitude), parseFloat(item.latitude)])),
          itemData: item,
        });
        feature.setStyle(createFeatureStyle(feature));
        vectorSourceRef.current.addFeature(feature);
      }
    });
  }, [data, createFeatureStyle]);

  useEffect(() => {
    if (!mapInstance.current) {
      mapInstance.current = new Map({
        target: mapRef.current,
        layers: [
          new TileLayer({
            source: new XYZ({
              url: 'https://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            }),
          }),
        ],
        view: new View({
          center: fromLonLat([-93.0977, 41.8780]),
          zoom: 7,
        }),
      });

      vectorSourceRef.current = new VectorSource();
      const clusterSource = new Cluster({
        distance: 50,
        source: vectorSourceRef.current,
      });

      vectorLayerRef.current = new VectorLayer({
        source: clusterSource,
        style: feature => {
          const size = feature.get('features').length;
          const featureCategories = feature.get('features').map(f => getCategoryFromUrl(f.get('itemData').url));
          return new Style({
            image: new Icon({
              src: generateSvgIcon('cluster', size, featureCategories),
              imgSize: [50, 50],
            }),
          });
        },
      });

      mapInstance.current.addLayer(vectorLayerRef.current);

      mapInstance.current.on('singleclick', async (event) => {
        mapInstance.current.forEachFeatureAtPixel(event.pixel, async (feature) => {
          const features = feature.get('features');
          if (features && features.length > 0) {
            console.log('MapComponent: Features clicked:', features);
            setPopupFeatures(features);
            setReferenceElement(event.coordinate);
            setPopupVisible(true);
            
            const itemIds = features.map(f => f.get('itemData').id);
            const newDetailedData = await onClusterClick(itemIds);
            setDetailedData(prevData => ({...prevData, ...newDetailedData}));
          } else {
            setPopupVisible(false);
          }
        });
      });
    }

    updateMapFeatures();
    mapInstance.current.updateSize();
  }, [updateMapFeatures, onClusterClick]);

  useEffect(() => {
    updateMapFeatures();
  }, [data, updateMapFeatures]);

  useEffect(() => {
    if (vectorSourceRef.current) {
      vectorSourceRef.current.getFeatures().forEach(feature => {
        feature.setStyle(createFeatureStyle(feature));
      });
      if (vectorLayerRef.current) {
        vectorLayerRef.current.changed();
      }
    }
  }, [updateTrigger, createFeatureStyle]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
      {popupVisible && (
        <div
          ref={popperElementRef}
          style={{ ...styles.popper, zIndex: 1000, position: 'absolute', top: 0, left: 0 }}
          {...attributes.popper}
        >
          <PopupContent
            features={popupFeatures.map(f => ({
              ...f.get('itemData'),
              ...detailedData[f.get('itemData').id]
            }))}
            onClose={() => setPopupVisible(false)}
            onFavorite={handleFavoriteClick}
            onRowClick={handleRowClick}
            selectedRows={selectedRows}
          />
        </div>
      )}
    </div>
  );
});

export default MapComponent;