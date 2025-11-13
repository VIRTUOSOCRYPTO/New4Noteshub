import { useState, useEffect, useRef } from "react";
import { Search, Clock, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { apiRequest } from "@/lib/api";
import { showToast } from "@/components/ui/toast-container";

interface SearchAutocompleteProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export default function SearchAutocomplete({ onSearch, placeholder = "Search notes..." }: SearchAutocompleteProps) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [history, setHistory] = useState<Array<{ id: string; query: string }>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const loadHistory = async () => {
    try {
      const data = await apiRequest<{ history: Array<{ id: string; query: string }> }>(
        "/api/search/history?limit=5"
      );
      setHistory(data.history);
    } catch (error) {
      console.error("Failed to load search history:", error);
    }
  };

  const loadSuggestions = async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest<{ suggestions: string[] }>(
        `/api/search/autocomplete?q=${encodeURIComponent(searchQuery)}&limit=8`
      );
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error("Failed to load suggestions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (value: string) => {
    setQuery(value);
    if (value.length >= 2) {
      loadSuggestions(value);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(value.length === 0 && history.length > 0);
    }
  };

  const handleSearch = (searchQuery: string) => {
    if (searchQuery.trim()) {
      onSearch(searchQuery);
      setQuery(searchQuery);
      setShowSuggestions(false);
      loadHistory(); // Refresh history
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSearch(query);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  };

  const clearHistory = async () => {
    try {
      await apiRequest("/api/search/history", { method: "DELETE" });
      setHistory([]);
      showToast("Search history cleared", "success");
    } catch (error) {
      showToast("Failed to clear history", "error");
    }
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <div className="relative">
        <Search 
          className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" 
          aria-hidden="true"
        />
        <Input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(query.length === 0 && history.length > 0 || suggestions.length > 0)}
          placeholder={placeholder}
          className="pl-10 pr-10"
          aria-label="Search notes"
          aria-autocomplete="list"
          aria-controls="search-suggestions"
          aria-expanded={showSuggestions}
          data-testid="search-input"
        />
        {query && (
          <button
            onClick={() => {
              setQuery("");
              setSuggestions([]);
              setShowSuggestions(false);
            }}
            className="absolute right-3 top-1/2 transform -translate-y-1/2"
            aria-label="Clear search"
            data-testid="clear-search-button"
          >
            <X className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {showSuggestions && (
        <div 
          id="search-suggestions"
          className="absolute z-50 w-full mt-2 bg-white border rounded-lg shadow-lg max-h-[400px] overflow-y-auto"
          role="listbox"
          data-testid="search-suggestions"
        >
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="py-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Suggestions
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={`suggestion-${index}`}
                  onClick={() => handleSearch(suggestion)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
                  role="option"
                  aria-selected={false}
                  data-testid={`suggestion-${index}`}
                >
                  <Search className="h-4 w-4 text-gray-400" aria-hidden="true" />
                  <span className="text-gray-800">{suggestion}</span>
                </button>
              ))}
            </div>
          )}

          {/* History */}
          {query.length === 0 && history.length > 0 && (
            <div className="py-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase flex justify-between items-center">
                <span>Recent Searches</span>
                <button
                  onClick={clearHistory}
                  className="text-blue-600 hover:text-blue-800 normal-case font-normal"
                  aria-label="Clear search history"
                  data-testid="clear-history-button"
                >
                  Clear
                </button>
              </div>
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleSearch(item.query)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
                  role="option"
                  aria-selected={false}
                  data-testid={`history-${item.id}`}
                >
                  <Clock className="h-4 w-4 text-gray-400" aria-hidden="true" />
                  <span className="text-gray-800">{item.query}</span>
                </button>
              ))}
            </div>
          )}

          {suggestions.length === 0 && (query.length === 0 ? history.length === 0 : true) && query.length >= 2 && !loading && (
            <div className="px-4 py-8 text-center text-gray-500">
              No suggestions found
            </div>
          )}

          {loading && (
            <div className="px-4 py-4 text-center text-gray-500">
              Loading suggestions...
            </div>
          )}
        </div>
      )}
    </div>
  );
}
