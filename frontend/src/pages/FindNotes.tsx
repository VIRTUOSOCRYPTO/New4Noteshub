import FilterSection from "@/components/notes/FilterSection";
import NotesList from "@/components/notes/NotesList";
import SearchAutocomplete from "@/components/search/SearchAutocomplete";
import SavedSearches from "@/components/search/SavedSearches";
import { useState } from "react";
import { SearchNotesParams } from "@/lib/schema";
import { Search, Filter, BookOpen, TrendingUp, Building2 } from "lucide-react";
import { usePageVisits } from "@/hooks/use-page-visits";
import { apiRequest } from "@/lib/api";
import { showToast } from "@/components/ui/toast-container";
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
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-slate-900 rounded-lg flex items-center justify-center">
                <Search className="h-7 w-7 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-slate-900">
                  Browse Repository
                </h1>
                <p className="text-slate-600 text-lg mt-1">Search and discover academic resources</p>
              </div>
            </div>
            
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="hidden md:flex border-slate-300 hover:bg-slate-100"
            >
              <Filter className="mr-2 h-5 w-5" />
              {showFilters ? 'Hide' : 'Show'} Filters
            </Button>
          </div>

          {/* Search Bar */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
            <SearchAutocomplete onSearch={handleSearch} placeholder="Search by title, subject, department..." />
            {searchQuery && (
              <div className="mt-4 flex items-center gap-2">
                <span className="text-sm text-slate-600">
                  Showing results for: <strong className="text-slate-900">"

{searchQuery}"</strong>
                </span>
                <button
                  onClick={clearSearch}
                  className="text-sm text-blue-600 hover:text-blue-800 underline font-medium"
                  data-testid="clear-search"
                >
                  Clear search
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Saved Searches */}
        <div className="mb-8">
          <SavedSearches 
            onSearch={handleSearch} 
            currentQuery={searchQuery}
            currentFilters={filters}
          />
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Total Notes", value: "1,234", icon: BookOpen },
            { label: "Active Users", value: "567", icon: TrendingUp },
            { label: "Departments", value: "12", icon: Building2 },
            { label: "Downloads", value: "8.9K", icon: TrendingUp }
          ].map((stat, i) => (
            <div
              key={i}
              className="bg-white rounded-lg p-6 shadow-sm border border-slate-200 text-center hover:shadow-md transition-shadow"
            >
              <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <stat.icon className="h-6 w-6 text-slate-700" />
              </div>
              <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
              <div className="text-sm text-slate-600">{stat.label}</div>
            </div>
          ))}
        </div>
        
        {/* Filters Section */}
        {showFilters && (
          <div className="mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
              <FilterSection onFilter={handleFilter} />
            </div>
          </div>
        )}
        
        {/* Results */}
        <div>
          {searchQuery && searchResults.length > 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-8 border border-slate-200">
              <h2 className="text-2xl font-bold mb-6 text-slate-900">
                Search Results <span className="text-blue-600">({searchResults.length})</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {searchResults.map((note, index) => (
                  <div
                    key={note.id}
                    className="bg-slate-50 rounded-lg p-6 hover:shadow-md transition-shadow border border-slate-200"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 bg-slate-900 rounded-lg flex items-center justify-center">
                        <BookOpen className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <h3 className="font-bold text-lg mb-2 text-slate-900">{note.title}</h3>
                    <p className="text-sm text-slate-600 mb-4">
                      {note.department} • {note.subject}
                    </p>
                    <div className="flex gap-4 text-sm text-slate-500">
                      <span>📥 {note.downloadCount}</span>
                      <span>👁 {note.viewCount}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : searchQuery && !isSearching ? (
            <div className="bg-white rounded-lg shadow-sm p-12 border border-slate-200 text-center">
              <Search className="h-20 w-20 mx-auto mb-6 text-slate-300" />
              <p className="text-xl text-slate-600">No notes found matching your search</p>
            </div>
          ) : (
            <NotesList filters={filters} />
          )}
          
          {isSearching && (
            <div className="bg-white rounded-lg shadow-sm p-12 border border-slate-200 text-center">
              <div className="inline-block w-16 h-16 border-4 border-slate-200 border-t-slate-900 rounded-full animate-spin" />
              <p className="mt-6 text-slate-600 text-lg">Searching repository...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
