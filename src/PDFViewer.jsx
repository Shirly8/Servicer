import React from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';

const PDFViewer = ({ file }) => {
  console.log(file);
  return (
    <div style={{ height: '750px', border: '1px solid red' }}>
      {/* Use the matching CDN version for pdf.worker.js */}
      <Worker workerUrl={`https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`}>
        <Viewer fileUrl={file} />
      </Worker>
    </div>
  );
};

export default PDFViewer;
