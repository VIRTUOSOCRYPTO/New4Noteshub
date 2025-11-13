import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Bookmark, Trash2, Search as SearchIcon } from "lucide-react";
import { apiRequest } from "@/lib/api";
import { showToast } from "@/components/ui/toast-container";

interface SavedSearch {
  id: string;
  name: string;
  query: string;
  filters: Record<string, any>;
  created_at: string;
}

interface SavedSearchesProps {
  onSearch: (query: string, filters: Record<string, any>) => void;
  currentQuery?: string;
  currentFilters?: Record<string, any>;
}

export default function SavedSearches({ onSearch, currentQuery, currentFilters }: SavedSearchesProps) {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [searchName, setSearchName] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSavedSearches();
  }, []);

  const loadSavedSearches = async () => {
    try {
      const data = await apiRequest<{ searches: SavedSearch[] }>("/api/search/saved");
      setSavedSearches(data.searches);
    } catch (error) {
      console.error("Failed to load saved searches:", error);
    }
  };

  const handleSaveSearch = async () => {
    if (!searchName.trim()) {
      showToast("Please enter a name for this search", "error");
      return;
    }

    if (!currentQuery) {
      showToast("No active search to save", "error");
      return;
    }

    setLoading(true);
    try {
      await apiRequest("/api/search/saved", {
        method: "POST",
        body: JSON.stringify({
          name: searchName,
          query: currentQuery,
          filters: currentFilters || {}
        }),
        headers: { "Content-Type": "application/json" }
      });

      showToast("Search saved successfully", "success");
      setShowSaveDialog(false);
      setSearchName("");
      loadSavedSearches();
    } catch (error) {
      showToast("Failed to save search", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSearch = async (searchId: string) => {
    if (!confirm("Are you sure you want to delete this saved search?")) {
      return;
    }

    try {
      await apiRequest(`/api/search/saved/${searchId}`, { method: "DELETE" });
      showToast("Search deleted", "success");
      loadSavedSearches();
    } catch (error) {
      showToast("Failed to delete search", "error");
    }
  };

  const handleUseSearch = (search: SavedSearch) => {
    onSearch(search.query, search.filters);
  };

  return (
    <Card data-testid="saved-searches">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Bookmark className="h-5 w-5" aria-hidden="true" />
              Saved Searches
            </CardTitle>
            <CardDescription>Quick access to your favorite searches</CardDescription>
          </div>
          {currentQuery && (
            <Button
              onClick={() => setShowSaveDialog(true)}
              size="sm"
              data-testid="save-current-search-button"
              aria-label="Save current search"
            >
              <Bookmark className="h-4 w-4 mr-2" aria-hidden="true" />
              Save Current Search
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {savedSearches.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Bookmark className="h-12 w-12 mx-auto mb-4 text-gray-300" aria-hidden="true" />
            <p>No saved searches yet</p>
            <p className="text-sm mt-2">Perform a search and save it for quick access later</p>
          </div>
        ) : (
          <div className="space-y-3">
            {savedSearches.map((search) => (
              <div
                key={search.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                data-testid={`saved-search-${search.id}`}
              >
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800">{search.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    Query: "{search.query}"
                    {Object.keys(search.filters).length > 0 && (
                      <span className="ml-2 text-xs text-gray-500">
                        (+{Object.keys(search.filters).length} filters)
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleUseSearch(search)}
                    data-testid={`use-search-${search.id}`}
                    aria-label={`Use search: ${search.name}`}
                  >
                    <SearchIcon className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeleteSearch(search.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    data-testid={`delete-search-${search.id}`}
                    aria-label={`Delete search: ${search.name}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Save Search Dialog */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent data-testid="save-search-dialog">
          <DialogHeader>
            <DialogTitle>Save Search</DialogTitle>
            <DialogDescription>
              Give your search a name to easily access it later
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="search-name">Search Name</Label>
              <Input
                id="search-name"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="e.g., Computer Science Notes"
                data-testid="search-name-input"
                aria-label="Search name"
              />
            </div>
            <div className="space-y-2">
              <Label>Query</Label>
              <p className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                "{currentQuery}"
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveSearch} disabled={loading} data-testid="confirm-save-button">
              {loading ? "Saving..." : "Save Search"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
