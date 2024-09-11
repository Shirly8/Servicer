import React from 'react';
import {Viewer} from '@react-pdf-viewer/core';  //Core Viewer
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout'; //Plugin

// Import styles
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

const defaultLayout = defaultLayoutPlugin();


const PdfViewer = ({ file }) => {
  return (
    <div style={{ height: '750px' }}>
        <Viewer fileUrl={file} 
        plugins = {[defaultLayout]}
        
        
        
        />

    </div>
  );
};

export default PdfViewer
