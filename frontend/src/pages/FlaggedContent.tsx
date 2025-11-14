import { useState, useEffect } from "react";
import { apiRequest } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, XCircle, FileText, Calendar, User, Flag } from "lucide-react";
import { showToast } from "@/components/ui/toast-container";
import { motion, AnimatePresence } from "framer-motion";
import { queryClient } from "@/lib/queryClient";

interface FlaggedNote {
  id: string;
  title: string;
  subject: string;
  department: string;
  usn: string;
  flag_reason: string;
  uploaded_at: string;
  filename: string;
}

export default function FlaggedContent() {
  const [flaggedNotes, setFlaggedNotes] = useState<FlaggedNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState<string | null>(null);

  useEffect(() => {
    loadFlaggedNotes();
  }, []);

  const loadFlaggedNotes = async () => {
    try {
      setLoading(true);
      const data = await apiRequest<FlaggedNote[]>("/api/notes/flagged");
      setFlaggedNotes(data);
    } catch (error: any) {
      showToast(error.message || "Failed to load flagged content", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (noteId: string, approved: boolean) => {
    try {
      setReviewing(noteId);
      await apiRequest("POST", `/api/notes/${noteId}/review`, { approved });
      showToast(
        approved ? "Note has been approved" : "Note has been rejected and removed",
        "success"
      );
      setFlaggedNotes(flaggedNotes.filter(note => note.id !== noteId));
      queryClient.invalidateQueries({ queryKey: ['/api/notes'] });
    } catch (error: any) {
      showToast(error.message || "Failed to review note", "error");
    } finally {
      setReviewing(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          className="absolute top-20 left-10 w-40 h-40 bg-gradient-to-br from-red-400 to-orange-500 rounded-full opacity-20 blur-3xl"
          animate={{ y: [0, -30, 0], x: [0, 20, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-20 right-20 w-56 h-56 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full opacity-20 blur-3xl"
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
              whileHover={{ rotate: 360, scale: 1.1 }}
              transition={{ duration: 0.5 }}
              className="w-16 h-16 bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg"
            >
              <Flag className="h-8 w-8 text-white" />
            </motion.div>
            <div>
              <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-600 to-orange-600">
                Content Moderation
              </h1>
              <p className="text-gray-600 text-lg mt-1">Review and manage flagged content</p>
            </div>
          </div>

          {/* Stats Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white/20"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-white" />
                </div>
                <div>
                  <div className="text-3xl font-bold text-gray-900">{flaggedNotes.length}</div>
                  <div className="text-sm text-gray-600">Pending Reviews</div>
                </div>
              </div>
              {flaggedNotes.length === 0 && (
                <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
                  All Clear! ✓
                </Badge>
              )}
            </div>
          </motion.div>
        </motion.div>

        {/* Flagged Notes List */}
        {flaggedNotes.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-white/80 backdrop-blur-xl rounded-3xl p-16 shadow-xl border border-white/20 text-center"
          >
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-24 h-24 bg-gradient-to-br from-green-400 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <CheckCircle className="h-12 w-12 text-white" />
            </motion.div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">All Caught Up!</h3>
            <p className="text-gray-600 text-lg">No flagged content to review at the moment</p>
          </motion.div>
        ) : (
          <div className="space-y-6">
            <AnimatePresence>
              {flaggedNotes.map((note, index) => (
                <motion.div
                  key={note.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  whileHover={{ scale: 1.02 }}
                >
                  <Card className="bg-white/80 backdrop-blur-xl border-red-200 shadow-xl hover:shadow-2xl transition-all duration-300">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center">
                              <FileText className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <CardTitle className="text-xl">{note.title}</CardTitle>
                              <CardDescription className="flex items-center space-x-2 mt-1">
                                <span>{note.department}</span>
                                <span>•</span>
                                <span>{note.subject}</span>
                              </CardDescription>
                            </div>
                          </div>
                        </div>
                        <Badge variant="destructive" className="ml-4">
                          <Flag className="h-3 w-3 mr-1" />
                          Flagged
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {/* Info Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-xl">
                          <div className="flex items-center space-x-2">
                            <User className="h-4 w-4 text-gray-500" />
                            <div>
                              <div className="text-xs text-gray-500">Uploaded by</div>
                              <div className="font-medium text-gray-900">{note.usn}</div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Calendar className="h-4 w-4 text-gray-500" />
                            <div>
                              <div className="text-xs text-gray-500">Upload Date</div>
                              <div className="font-medium text-gray-900">
                                {new Date(note.uploaded_at).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <FileText className="h-4 w-4 text-gray-500" />
                            <div>
                              <div className="text-xs text-gray-500">File</div>
                              <div className="font-medium text-gray-900 truncate">{note.filename}</div>
                            </div>
                          </div>
                        </div>

                        {/* Flag Reason */}
                        <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                          <div className="flex items-start space-x-2">
                            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                            <div>
                              <div className="text-sm font-medium text-red-900 mb-1">Flag Reason:</div>
                              <div className="text-sm text-red-800">{note.flag_reason}</div>
                            </div>
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex justify-end space-x-3 pt-4">
                          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                              variant="outline"
                              className="border-green-300 text-green-700 hover:bg-green-50"
                              onClick={() => handleReview(note.id, true)}
                              disabled={reviewing === note.id}
                            >
                              <CheckCircle className="mr-2 h-4 w-4" />
                              Approve
                            </Button>
                          </motion.div>
                          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                              variant="destructive"
                              onClick={() => handleReview(note.id, false)}
                              disabled={reviewing === note.id}
                            >
                              <XCircle className="mr-2 h-4 w-4" />
                              Reject & Remove
                            </Button>
                          </motion.div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
