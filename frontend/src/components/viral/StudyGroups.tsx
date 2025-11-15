import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Users, Plus, MessageCircle, Calendar, TrendingUp } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface StudyGroup {
  id: string;
  name: string;
  description?: string;
  subject?: string;
  created_by: string;
  created_at: string;
  is_private: boolean;
  member_count: number;
  max_members: number;
}

export function StudyGroups() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    subject: "",
    is_private: false,
    max_members: 50
  });

  // Fetch user's groups
  const { data: myGroupsData, isLoading } = useQuery({
    queryKey: ["/api/study-groups/my-groups"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/study-groups/my-groups");
      return await res.json();
    },
  });

  // Fetch discover groups
  const { data: discoverData } = useQuery({
    queryKey: ["/api/study-groups/discover"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/study-groups/discover");
      return await res.json();
    },
  });

  // Create group mutation
  const createGroupMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const res = await apiRequest("POST", "/api/study-groups/create", data);
      return await res.json();
    },
    onSuccess: () => {
      toast({
        title: "Success!",
        description: "Study group created successfully! +50 points 🎉",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/study-groups/my-groups"] });
      setIsCreateDialogOpen(false);
      setFormData({
        name: "",
        description: "",
        subject: "",
        is_private: false,
        max_members: 50
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create study group",
        variant: "destructive",
      });
    },
  });

  // Join group mutation
  const joinGroupMutation = useMutation({
    mutationFn: async (groupId: string) => {
      const res = await apiRequest("POST", `/api/study-groups/${groupId}/join`);
      return await res.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Success!",
        description: data.message || "Joined group successfully!",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/study-groups/my-groups"] });
      queryClient.invalidateQueries({ queryKey: ["/api/study-groups/discover"] });
    },
  });

  const handleCreateGroup = () => {
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Group name is required",
        variant: "destructive",
      });
      return;
    }
    createGroupMutation.mutate(formData);
  };

  const myGroups: StudyGroup[] = myGroupsData?.groups || [];
  const discoverGroups: StudyGroup[] = discoverData?.groups || [];

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading study groups...</div>;
  }

  return (
    <div className="space-y-6" data-testid="study-groups">
      {/* Header with Create Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Study Groups</h2>
          <p className="text-muted-foreground">Collaborate with friends and compete</p>
        </div>

        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="create-group-button">
              <Plus className="h-4 w-4 mr-2" />
              Create Group
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Study Group</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Group Name *</Label>
                <Input
                  id="name"
                  placeholder="e.g., CSE 2024 Exam Prep"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  data-testid="group-name-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject (Optional)</Label>
                <Input
                  id="subject"
                  placeholder="e.g., Data Structures"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="What's this group about?"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_members">Max Members</Label>
                <Input
                  id="max_members"
                  type="number"
                  min={2}
                  max={200}
                  value={formData.max_members}
                  onChange={(e) => setFormData({ ...formData, max_members: parseInt(e.target.value) || 50 })}
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_private"
                  checked={formData.is_private}
                  onChange={(e) => setFormData({ ...formData, is_private: e.target.checked })}
                  className="h-4 w-4"
                />
                <Label htmlFor="is_private">Private Group (invite only)</Label>
              </div>

              <Button 
                onClick={handleCreateGroup} 
                disabled={createGroupMutation.isPending}
                className="w-full"
                data-testid="create-group-submit"
              >
                {createGroupMutation.isPending ? "Creating..." : "Create Group"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* My Groups */}
      <div>
        <h3 className="text-lg font-semibold mb-4">My Groups ({myGroups.length})</h3>
        {myGroups.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">You haven't joined any groups yet</p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Group
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {myGroups.map((group) => (
              <Card key={group.id} className="hover:shadow-lg transition-shadow" data-testid={`my-group-${group.id}`}>
                <CardHeader>
                  <CardTitle className="text-base flex items-start justify-between">
                    <span className="line-clamp-1">{group.name}</span>
                    {group.is_private && (
                      <Badge variant="secondary" className="text-xs">Private</Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {group.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {group.description}
                    </p>
                  )}

                  {group.subject && (
                    <Badge variant="outline">{group.subject}</Badge>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Users className="h-4 w-4" />
                      <span>{group.member_count}/{group.max_members}</span>
                    </div>
                  </div>

                  <Button 
                    className="w-full" 
                    size="sm"
                    onClick={() => {
                      // Navigate to group detail page (to be implemented)
                      window.location.href = `/study-groups/${group.id}`;
                    }}
                    data-testid={`open-group-${group.id}`}
                  >
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Open Group
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Discover Public Groups */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Discover Groups
        </h3>
        {discoverGroups.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-muted-foreground">No public groups available yet</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {discoverGroups.map((group) => (
              <Card key={group.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-base">{group.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {group.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {group.description}
                    </p>
                  )}

                  {group.subject && (
                    <Badge variant="outline">{group.subject}</Badge>
                  )}

                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>{group.member_count}/{group.max_members} members</span>
                  </div>

                  <Button 
                    className="w-full" 
                    size="sm"
                    onClick={() => joinGroupMutation.mutate(group.id)}
                    disabled={joinGroupMutation.isPending}
                    data-testid={`join-group-${group.id}`}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Join Group
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
