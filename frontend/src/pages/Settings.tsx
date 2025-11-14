import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Key, Bell, Eye, EyeOff, Upload, Camera, UserCircle, Settings as SettingsIcon, Shield, User } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useState, useEffect, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { showToast } from "@/components/ui/toast-container";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { motion } from "framer-motion";

export default function Settings() {
  const { user, isLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [notifyNewNotes, setNotifyNewNotes] = useState(false);
  const [notifyDownloads, setNotifyDownloads] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const updateSettingsMutation = useMutation({
    mutationFn: (settings: { notifyNewNotes?: boolean, notifyDownloads?: boolean }) => {
      return apiRequest('PATCH', '/api/user/settings', settings);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/user'] });
      showToast('Settings updated successfully', 'success');
    },
    onError: (error) => {
      showToast(`Failed to update settings: ${error.message}`, 'error');
    }
  });

  const updatePasswordMutation = useMutation({
    mutationFn: () => {
      if (newPassword !== confirmPassword) {
        throw new Error('New passwords do not match');
      }
      return apiRequest('PATCH', '/api/user/password', {
        currentPassword,
        newPassword,
        confirmNewPassword: confirmPassword,
      });
    },
    onSuccess: () => {
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      showToast('Password updated successfully', 'success');
    },
    onError: (error) => {
      showToast(`Failed to update password: ${error.message}`, 'error');
    }
  });

  function handleSaveNotifications() {
    updateSettingsMutation.mutate({ notifyNewNotes, notifyDownloads });
  }

  function handleUpdatePassword() {
    if (!currentPassword) {
      showToast('Please enter your current password', 'error');
      return;
    }
    if (!newPassword) {
      showToast('Please enter a new password', 'error');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('New passwords do not match', 'error');
      return;
    }
    updatePasswordMutation.mutate();
  }

  function handleProfilePictureChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (file.size > 2 * 1024 * 1024) {
      showToast('File size must be less than 2MB', 'error');
      return;
    }
    
    const formData = new FormData();
    formData.append('profilePicture', file);
    setIsUploading(true);
    
    const token = localStorage.getItem('auth_token');
    fetch('/api/user/profile-picture', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData,
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to upload profile picture');
        return response.json();
      })
      .then(() => {
        queryClient.invalidateQueries({ queryKey: ['/api/user'] });
        showToast('Profile picture updated successfully', 'success');
      })
      .catch(error => {
        showToast(`Error: ${error.message}`, 'error');
      })
      .finally(() => {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      });
  }
  
  useEffect(() => {
    if (user) {
      setNotifyNewNotes(user.notifyNewNotes ?? true);
      setNotifyDownloads(user.notifyDownloads ?? false);
    }
  }, [user]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full"
        />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium">You need to be logged in to view settings.</h3>
        </div>
      </div>
    );
  }

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
          <div className="flex items-center space-x-4 mb-6">
            <motion.div
              whileHover={{ rotate: 180, scale: 1.1 }}
              transition={{ duration: 0.5 }}
              className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg"
            >
              <SettingsIcon className="h-8 w-8 text-white" />
            </motion.div>
            <div>
              <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                Settings
              </h1>
              <p className="text-gray-600 text-lg mt-1">Manage your account preferences</p>
            </div>
          </div>
        </motion.div>

        {/* Settings Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Tabs defaultValue="account" className="space-y-6">
            <TabsList className="bg-white/80 backdrop-blur-xl border border-white/20 shadow-lg p-1">
              <TabsTrigger value="account" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-purple-500 data-[state=active]:text-white">
                <User className="h-4 w-4 mr-2" />
                Account
              </TabsTrigger>
              <TabsTrigger value="profile" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-purple-500 data-[state=active]:text-white">
                <Camera className="h-4 w-4 mr-2" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="security" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-purple-500 data-[state=active]:text-white">
                <Shield className="h-4 w-4 mr-2" />
                Security
              </TabsTrigger>
              <TabsTrigger value="notifications" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-purple-500 data-[state=active]:text-white">
                <Bell className="h-4 w-4 mr-2" />
                Notifications
              </TabsTrigger>
            </TabsList>
            
            {/* Account Tab */}
            <TabsContent value="account">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-2xl flex items-center">
                      <User className="h-6 w-6 mr-2 text-blue-500" />
                      Account Information
                    </CardTitle>
                    <CardDescription>Your registered account details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="usn" className="text-sm font-medium text-gray-700">USN</Label>
                        <div className="relative">
                          <Input id="usn" defaultValue={user.usn} disabled className="bg-gray-50 pl-10" />
                          <UserCircle className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                        </div>
                        <p className="text-xs text-gray-500">Cannot be changed after registration</p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="department" className="text-sm font-medium text-gray-700">Department</Label>
                        <div className="relative">
                          <Input id="department" defaultValue={user.department} disabled className="bg-gray-50 pl-10" />
                          <Shield className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                        </div>
                        <p className="text-xs text-gray-500">Cannot be changed after registration</p>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="createdAt" className="text-sm font-medium text-gray-700">Member Since</Label>
                        <Input 
                          id="createdAt" 
                          value={new Date(user.createdAt).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} 
                          disabled 
                          className="bg-gray-50"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>
            
            {/* Profile Picture Tab */}
            <TabsContent value="profile">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-2xl flex items-center">
                      <Camera className="h-6 w-6 mr-2 text-purple-500" />
                      Profile Picture
                    </CardTitle>
                    <CardDescription>Update your profile photo</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex flex-col items-center space-y-6">
                      <motion.div
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <Avatar className="h-32 w-32 border-4 border-white shadow-2xl">
                          <AvatarImage 
                            src={user.profilePicture ? `/api/user/profile-picture/${user.profilePicture}` : undefined} 
                            alt={user.usn} 
                          />
                          <AvatarFallback className="text-3xl bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                            {user.usn?.substring(0, 2).toUpperCase() || "UN"}
                          </AvatarFallback>
                        </Avatar>
                      </motion.div>
                      
                      <div className="flex flex-col items-center gap-3">
                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                          <Button 
                            variant="outline" 
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isUploading}
                            className="border-2 border-purple-300 hover:bg-purple-50"
                          >
                            {isUploading ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Uploading...
                              </>
                            ) : (
                              <>
                                <Camera className="mr-2 h-4 w-4" />
                                Change Picture
                              </>
                            )}
                          </Button>
                        </motion.div>
                        <input 
                          type="file" 
                          ref={fileInputRef}
                          className="hidden" 
                          accept="image/*"
                          onChange={handleProfilePictureChange}
                        />
                        <p className="text-sm text-gray-500 text-center">
                          JPG, PNG or GIF. Max size 2MB.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>
            
            {/* Security Tab */}
            <TabsContent value="security">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-2xl flex items-center">
                      <Shield className="h-6 w-6 mr-2 text-green-500" />
                      Security Settings
                    </CardTitle>
                    <CardDescription>Manage your password and security</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="current-password">Current Password</Label>
                        <div className="relative">
                          <Input 
                            id="current-password" 
                            type={showPassword ? "text" : "password"}
                            placeholder="Enter your current password" 
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            className="pr-10"
                          />
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="absolute right-0 top-0" 
                            onClick={() => setShowPassword(!showPassword)}
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="new-password">New Password</Label>
                        <Input 
                          id="new-password" 
                          type={showPassword ? "text" : "password"}
                          placeholder="Enter your new password" 
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm New Password</Label>
                        <Input 
                          id="confirm-password" 
                          type={showPassword ? "text" : "password"}
                          placeholder="Confirm your new password" 
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button 
                        onClick={handleUpdatePassword}
                        disabled={updatePasswordMutation.isPending}
                        className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                      >
                        {updatePasswordMutation.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Updating...
                          </>
                        ) : (
                          <>
                            <Key className="mr-2 h-4 w-4" />
                            Update Password
                          </>
                        )}
                      </Button>
                    </motion.div>
                  </CardFooter>
                </Card>
              </motion.div>
            </TabsContent>
            
            {/* Notifications Tab */}
            <TabsContent value="notifications">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="bg-white/80 backdrop-blur-xl border-white/20 shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-2xl flex items-center">
                      <Bell className="h-6 w-6 mr-2 text-orange-500" />
                      Notification Preferences
                    </CardTitle>
                    <CardDescription>Manage how you receive notifications</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <motion.div
                      whileHover={{ x: 5 }}
                      className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-100"
                    >
                      <div className="space-y-1 flex-1">
                        <Label htmlFor="notify-new-notes" className="text-base font-medium">New Notes in Department</Label>
                        <p className="text-sm text-gray-600">
                          Get notified when new notes are uploaded in your department
                        </p>
                      </div>
                      <Switch
                        id="notify-new-notes"
                        checked={notifyNewNotes}
                        onCheckedChange={setNotifyNewNotes}
                      />
                    </motion.div>
                    <Separator />
                    <motion.div
                      whileHover={{ x: 5 }}
                      className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-100"
                    >
                      <div className="space-y-1 flex-1">
                        <Label htmlFor="notify-downloads" className="text-base font-medium">Download Notifications</Label>
                        <p className="text-sm text-gray-600">
                          Get notified when someone downloads your notes
                        </p>
                      </div>
                      <Switch
                        id="notify-downloads"
                        checked={notifyDownloads}
                        onCheckedChange={setNotifyDownloads}
                      />
                    </motion.div>
                  </CardContent>
                  <CardFooter>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button 
                        onClick={handleSaveNotifications}
                        disabled={updateSettingsMutation.isPending}
                        className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                      >
                        {updateSettingsMutation.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Bell className="mr-2 h-4 w-4" />
                            Save Preferences
                          </>
                        )}
                      </Button>
                    </motion.div>
                  </CardFooter>
                </Card>
              </motion.div>
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </div>
  );
}
