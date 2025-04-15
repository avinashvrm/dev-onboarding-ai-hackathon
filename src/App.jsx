import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// API base URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// Collection colors for badges
const COLLECTION_COLORS = {
  slack: { bg: 'bg-purple-100 dark:bg-purple-900', text: 'text-purple-800 dark:text-purple-200', border: 'border-purple-200 dark:border-purple-800' },
  docs: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-800 dark:text-blue-200', border: 'border-blue-200 dark:border-blue-800' },
  codebase: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200', border: 'border-green-200 dark:border-green-800' },
  global: { bg: 'bg-gray-100 dark:bg-gray-800', text: 'text-gray-800 dark:text-gray-300', border: 'border-gray-200 dark:border-gray-700' },
};

function App() {
  const [collections, setCollections] = useState([]);
  const [queryInput, setQueryInput] = useState('');
  const [selectedCollection, setSelectedCollection] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    // Initialize from localStorage or user preference
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode !== null) {
      return savedMode === 'true';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Apply dark mode class to document
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // Fetch available collections on load
  useEffect(() => {
    fetchCollections();
  }, []);

  // Make sure slack is not selected
  useEffect(() => {
    if (selectedCollection === 'slack') {
      setSelectedCollection('');
    }
  }, [selectedCollection]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const fetchCollections = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/collections`);
      setCollections(response.data.collections);
      if (response.data.collections.length > 0) {
        // Select first non-slack collection, or empty if only slack exists
        const nonSlackCollections = response.data.collections.filter(c => c !== 'slack');
        if (nonSlackCollections.length > 0) {
          setSelectedCollection(nonSlackCollections[0]);
        } else {
          setSelectedCollection('');
        }
      }
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!queryInput.trim()) return;

    setIsLoading(true);
    setQueryResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query: queryInput,
        collection: selectedCollection === 'all' ? null : selectedCollection,
        top_k: 5
      });
      setQueryResults(response.data);
    } catch (error) {
      console.error('Error querying:', error);
      setQueryResults({
        answer: 'Error retrieving response. Please try again.',
        sources: []
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 text-slate-800 dark:text-slate-200 transition-colors duration-300">
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 dark:from-blue-800 dark:to-indigo-900 text-white shadow-lg relative">
        <div className="container mx-auto px-6 py-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold tracking-tight">
                <span className="text-blue-200">baby</span>steps<span className="text-blue-200">.ai</span>
              </h1>
              <p className="text-blue-100 mt-2 text-lg font-light tracking-wide">Ask questions to interact with your knowledge base</p>
            </div>
            <button 
              onClick={toggleDarkMode}
              className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-all duration-200"
              aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {darkMode ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-6 py-10">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl p-8 border border-slate-200 dark:border-slate-700 transition-all duration-300 hover:shadow-2xl">
            <div>
              <h2 className="text-2xl font-semibold mb-6 text-slate-800 dark:text-slate-200 border-b border-slate-200 dark:border-slate-700 pb-3">Query Knowledge Base</h2>
              <form onSubmit={handleQuerySubmit} className="space-y-6">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 mb-3 font-medium">Select Knowledge Source:</label>
                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => setSelectedCollection('')}
                      className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                        selectedCollection === '' 
                          ? 'bg-blue-50 dark:bg-blue-900/50 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 shadow-sm' 
                          : 'bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600'
                      }`}
                    >
                      All Collections
                    </button>
                    
                    {collections.filter(collection => collection !== 'slack').map((collection) => (
                      <button
                        key={collection}
                        type="button"
                        onClick={() => setSelectedCollection(collection)}
                        className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                          selectedCollection === collection 
                            ? 'bg-blue-50 dark:bg-blue-900/50 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 shadow-sm' 
                            : 'bg-white dark:bg-slate-700 border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600'
                        }`}
                      >
                        <span className={`inline-block w-3 h-3 rounded-full mr-2 ${COLLECTION_COLORS[collection]?.bg || 'bg-slate-300 dark:bg-slate-600'}`}></span>
                        {collection.charAt(0).toUpperCase() + collection.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 mb-3 font-medium">Your Question:</label>
                  <textarea
                    className="w-full p-4 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-3 focus:ring-blue-200 dark:focus:ring-blue-800 focus:border-blue-500 dark:focus:border-blue-700 transition-all duration-200 text-slate-700 dark:text-slate-200 resize-none shadow-sm bg-white dark:bg-slate-700"
                    rows="4"
                    value={queryInput}
                    onChange={(e) => setQueryInput(e.target.value)}
                    placeholder="What would you like to know?"
                  />
                </div>
                
                <button
                  type="submit"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-700 dark:to-indigo-700 text-white px-8 py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 dark:hover:from-blue-800 dark:hover:to-indigo-800 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center shadow-md hover:shadow-lg"
                  disabled={isLoading || !queryInput.trim()}
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Submit Question
                    </>
                  )}
                </button>
              </form>
              
              {queryResults && (
                <div className="mt-12 border-t border-slate-200 dark:border-slate-700 pt-8 animate-fadeIn">
                  <h3 className="text-xl font-semibold mb-4 text-slate-800 dark:text-slate-200">Answer:</h3>
                  <div className="bg-gradient-to-r from-blue-50 to-white dark:from-blue-900/30 dark:to-slate-800 p-6 rounded-lg border border-blue-100 dark:border-blue-900 shadow-sm">
                    <ReactMarkdown
                      components={{
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={atomDark}
                              language={match[1]}
                              PreTag="div"
                              className="rounded-md my-3 shadow-lg"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={`${className} bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-slate-800 dark:text-slate-200`} {...props}>
                              {children}
                            </code>
                          );
                        },
                        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold my-4 dark:text-slate-200" {...props} />,
                        h2: ({ node, ...props }) => <h2 className="text-xl font-bold my-3 dark:text-slate-200" {...props} />,
                        h3: ({ node, ...props }) => <h3 className="text-lg font-bold my-2 dark:text-slate-200" {...props} />,
                        p: ({ node, ...props }) => <p className="my-2 dark:text-slate-300" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc pl-5 my-2 dark:text-slate-300" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal pl-5 my-2 dark:text-slate-300" {...props} />,
                        li: ({ node, ...props }) => <li className="my-1 dark:text-slate-300" {...props} />,
                      }}
                      className="text-slate-700 dark:text-slate-300 prose prose-blue dark:prose-invert max-w-none"
                    >
                      {queryResults.answer}
                    </ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      
      <footer className="mt-16 py-8 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 transition-colors duration-300">
        <div className="container mx-auto px-6 flex justify-center items-center">
          <div className="text-center">
            <h3 className="text-slate-800 dark:text-slate-200 font-bold text-lg">
              <span className="text-blue-600 dark:text-blue-400">baby</span>steps<span className="text-blue-600 dark:text-blue-400">.ai</span>
            </h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-2">Powered by Qdrant and OpenAI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App; 