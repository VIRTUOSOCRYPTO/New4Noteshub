import FilterSection from "@/components/notes/FilterSection";
import NotesList from "@/components/notes/NotesList";
import SearchAutocomplete from "@/components/search/SearchAutocomplete";
import SavedSearches from "@/components/search/SavedSearches";
import { useState } from "react";
import { SearchNotesParams } from "@/lib/schema";
import { Search } from "lucide-react";
import { usePageVisits } from "@/hooks/use-page-visits";
import { apiRequest } from "@/lib/api";
import { showToast } from "@/components/ui/toast-container";

export default function FindNotes() {
  // Track page visit for App Explorer achievement
  usePageVisits('find-notes');
  
  const [filters, setFilters] = useState<SearchNotesParams>({
    department: undefined,
    subject: undefined,
    showAllDepartments: false
  });
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleFilter = (newFilters: SearchNotesParams) => {
    setFilters(newFilters);
    // Clear search when filters change
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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex items-center space-x-2">
        <Search className="h-6 w-6 text-primary" aria-hidden="true" />
        <h1 className="text-2xl font-bold text-gray-800">Find Notes</h1>
      </div>
      
      {/* Search Bar */}
      <div className="mb-6">
        <SearchAutocomplete onSearch={handleSearch} placeholder="Search by title, subject, or department..." />
        {searchQuery && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-sm text-gray-600">
              Showing results for: <strong>"{searchQuery}"</strong>
            </span>
            <button
              onClick={clearSearch}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
              data-testid="clear-search"
            >
              Clear search
            </button>
          </div>
        )}
      </div>

      {/* Saved Searches */}
      <div className="mb-6">
        <SavedSearches 
          onSearch={handleSearch} 
          currentQuery={searchQuery}
          currentFilters={filters}
        />
      </div>
      
      <p className="text-gray-600 mb-8">Apply filters to find notes shared by other students</p>
      
      <FilterSection onFilter={handleFilter} />
      
      {/* Show search results or regular notes list */}
      {searchQuery && searchResults.length > 0 ? (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Search Results ({searchResults.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.map((note) => (
              <div key={note.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <h3 className="font-semibold text-lg mb-2">{note.title}</h3>
                <p className="text-sm text-gray-600 mb-2">
                  {note.department} • {note.subject}
                </p>
                <div className="flex gap-4 text-sm text-gray-500">
                  <span>Downloads: {note.download_count}</span>
                  <span>Views: {note.view_count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : searchQuery && !isSearching ? (
        <div className="text-center py-12 text-gray-500">
          <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" aria-hidden="true" />
          <p>No notes found matching your search</p>
        </div>
      ) : (
        <NotesList filters={filters} />
      )}
      
      {isSearching && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary" role="status" aria-label="Searching">
            <span className="sr-only">Searching...</span>
          </div>
          <p className="mt-4 text-gray-600">Searching...</p>
        </div>
      )}
    </div>
  );
}
