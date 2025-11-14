import FilterSection from "@/components/notes/FilterSection";
import NotesList from "@/components/notes/NotesList";
import SearchAutocomplete from "@/components/search/SearchAutocomplete";
import SavedSearches from "@/components/search/SavedSearches";
import { useState } from "react";
import { SearchNotesParams } from "@/lib/schema";
import { Search, Filter, BookOpen, TrendingUp } from "lucide-react";
import { usePageVisits } from "@/hooks/use-page-visits";
import { apiRequest } from "@/lib/api";
import { showToast } from "@/components/ui/toast-container";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export default function FindNotes() {
  usePageVisits('find-notes');
  
  const [filters, setFilters] = useState<SearchNotesParams>({
    department: undefined,
    subject: undefined,
    showAllDepartments: false
  });
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showFilters, setShowFilters] = useState(true);

  const handleFilter = (newFilters: SearchNotesParams) => {
    setFilters(newFilters);
    if (searchQuery) {
      performSearch(searchQuery, newFilters);
    }
  };

  const performSearch = async (query: string, customFilters?: SearchNotesParams) => {
    setIsSearching(true);
    setSearchQuery(query);
    
    try {
      const filtersToUse = customFilters || filters;
      const params = new URLSearchParams({ q: query });
      
      if (filtersToUse.department) params.append('department', filtersToUse.department);
      if (filtersToUse.subject) params.append('subject', filtersToUse.subject);
      
      const response = await apiRequest<{ results: any[] }>(`/api/search?${params.toString()}`);
      setSearchResults(response.results);
      
      if (response.results.length === 0) {
        showToast("No notes found for this search", "info");
      }
    } catch (error) {
      console.error("Search error:", error);
      showToast("Search failed. Please try again.", "error");
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearch = (query: string, savedFilters?: Record<string, any>) => {
    if (savedFilters) {
      const newFilters = {
        department: savedFilters.department,
        subject: savedFilters.subject,
        showAllDepartments: savedFilters.showAllDepartments || false
      };
      setFilters(newFilters);
      performSearch(query, newFilters);
    } else {
      performSearch(query);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setSearchResults([]);
    setIsSearching(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          className="absolute top-20 left-10 w-40 h-40 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full opacity-20 blur-3xl"
          animate={{ y: [0, -30, 0], x: [0, 20, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-20 right-20 w-56 h-56 bg-gradient-to-br from-pink-400 to-orange-500 rounded-full opacity-20 blur-3xl"
          animate={{ y: [0, 30, 0], x: [0, -20, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <div className="container mx-auto px-4 py-12 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <motion.div
                whileHover={{ rotate: 360, scale: 1.1 }}
                transition={{ duration: 0.5 }}
                className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg"
              >
                <Search className="h-8 w-8 text-white" />
              </motion.div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                  Discover Notes
                </h1>
                <p className="text-gray-600 text-lg mt-1">Find the perfect study materials for your needs</p>
              </div>
            </div>
            
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="hidden md:flex border-2 border-purple-200 hover:bg-purple-50"
              >
                <Filter className="mr-2 h-5 w-5" />
                {showFilters ? 'Hide' : 'Show'} Filters
              </Button>
            </motion.div>
          </div>

          {/* Search Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20"
          >
            <SearchAutocomplete onSearch={handleSearch} placeholder="Search by title, subject, department..." />
            {searchQuery && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 flex items-center gap-2"
              >
                <span className="text-sm text-gray-600">
                  Showing results for: <strong className="text-purple-600">"{searchQuery}"</strong>
                </span>
                <button
                  onClick={clearSearch}
                  className="text-sm text-blue-600 hover:text-blue-800 underline font-medium"
                  data-testid="clear-search"
                >
                  Clear search
                </button>
              </motion.div>
            )}
          </motion.div>
        </motion.div>

        {/* Saved Searches */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mb-8"
        >
          <SavedSearches 
            onSearch={handleSearch} 
            currentQuery={searchQuery}
            currentFilters={filters}
          />
        </motion.div>

        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          {[
            { label: "Total Notes", value: "1,234", icon: BookOpen, color: "from-blue-500 to-cyan-500" },
            { label: "Active Users", value: "567", icon: TrendingUp, color: "from-purple-500 to-pink-500" },
            { label: "Departments", value: "12", icon: Filter, color: "from-orange-500 to-red-500" },
            { label: "Downloads", value: "8.9K", icon: TrendingUp, color: "from-green-500 to-teal-500" }
          ].map((stat, i) => (
            <motion.div
              key={i}
              whileHover={{ scale: 1.05, y: -5 }}
              className="bg-white/80 backdrop-blur-xl rounded-xl p-6 shadow-lg border border-white/20 text-center"
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center mx-auto mb-3`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
        
        {/* Filters Section */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mb-8"
          >
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20">
              <FilterSection onFilter={handleFilter} />
            </div>
          </motion.div>
        )}
        
        {/* Results */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          {searchQuery && searchResults.length > 0 ? (
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">
                Search Results <span className="text-purple-600">({searchResults.length})</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {searchResults.map((note, index) => (
                  <motion.div
                    key={note.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    whileHover={{ scale: 1.05, y: -10 }}
                    className="bg-white rounded-xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                        <BookOpen className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <h3 className="font-bold text-lg mb-2 text-gray-900">{note.title}</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      {note.department} • {note.subject}
                    </p>
                    <div className="flex gap-4 text-sm text-gray-500">
                      <span>📥 {note.download_count}</span>
                      <span>👁 {note.view_count}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ) : searchQuery && !isSearching ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-12 border border-white/20 text-center"
            >
              <Search className="h-20 w-20 mx-auto mb-6 text-gray-300" />
              <p className="text-xl text-gray-600">No notes found matching your search</p>
            </motion.div>
          ) : (
            <NotesList filters={filters} />
          )}
          
          {isSearching && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-12 border border-white/20 text-center"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="inline-block w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full"
              />
              <p className="mt-6 text-gray-600 text-lg">Searching for the best notes...</p>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
