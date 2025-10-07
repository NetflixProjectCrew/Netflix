import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import MovieRow from './components/MovieRow';
import Settings from './components/Settings';
import Account from './components/Account';
import './App.css';

const rowTitles = [
  'Continue Watching',
  'Recommendation for You',
  'Top Detectives of This Year',
  'Top Thrillers of This Year',
  'Top Horrors of This Year'
];

function HomePage() {
  return (
    <div className="app">
      <Header />
      <main className="main">
        {rowTitles.map((title, index) => (
          <MovieRow key={index} title={title} />
        ))}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/account" element={<Account />} />
      </Routes>
    </Router>
  );
}

export default App;