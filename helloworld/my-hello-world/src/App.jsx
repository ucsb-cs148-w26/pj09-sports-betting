// src/App.jsx
import React from 'react';

function App() {
  return (
    <div style={{ 
      fontFamily: 'sans-serif', 
      textAlign: 'center', 
      padding: '40px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      margin: '20px'
    }}>
      <header>
        <nav>
          <strong>Welcome to Sports Betting</strong> 
        </nav>
      </header>
      
      <main>
        <h1>Hello, World!</h1>
        <p>This is the initial React deployment for Alvin's branch.</p>
      </main>

      <footer style={{ marginTop: '40px', fontSize: '0.8rem', color: '#666' }}>
        <p>Deployed via Vercel | CS Class 2026</p>
      </footer>
    </div>
  );
}

export default App;