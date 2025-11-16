import { Switch, Route } from "wouter";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/queryClient";
import { Toaster } from "@/components/ui/toaster";
import { lazy, Suspense } from "react";
import { AuthProvider } from "@/hooks/use-auth";
import { ThemeProvider } from "@/hooks/use-theme";
import { ProtectedRoute } from "@/lib/protected-route";

// Lazy load pages for better performance
const NotFound = lazy(() => import("@/pages/not-found"));
const Home = lazy(() => import("@/pages/Home"));
const Upload = lazy(() => import("@/pages/Upload"));
const FindNotes = lazy(() => import("@/pages/FindNotes"));
const AuthPage = lazy(() => import("@/pages/auth-page"));
const ResetPassword = lazy(() => import("@/pages/ResetPassword"));
const Profile = lazy(() => import("@/pages/Profile"));
const Settings = lazy(() => import("@/pages/Settings"));
const FlaggedContent = lazy(() => import("@/pages/FlaggedContent"));
const CorsDebug = lazy(() => import("@/pages/CorsDebug"));
const Analytics = lazy(() => import("@/pages/Analytics"));
const LeaderboardPage = lazy(() => import("@/pages/LeaderboardPage"));
const AdminPanel = lazy(() => import("@/pages/AdminPanel"));
const Header = lazy(() => import("@/components/layout/Header"));
const Footer = lazy(() => import("@/components/layout/Footer"));
const ToastContainer = lazy(() => import("@/components/ui/toast-container"));
const NoteBuddy = lazy(() => import("@/components/NoteBuddy"));

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200">
    <div className="relative">
      {/* Outer rotating ring with dots */}
      <div className="absolute -inset-8 animate-spin" style={{ animationDuration: '3s' }}>
        <div className="h-full w-full rounded-full border-2 border-transparent">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full shadow-lg"></div>
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-lg"></div>
        </div>
      </div>
      
      {/* Middle rotating ring */}
      <div className="absolute -inset-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900 border-r-slate-700" style={{ animationDuration: '1.5s' }}></div>
      
      {/* Pulsing glow effect */}
      <div className="absolute inset-0 animate-pulse rounded-lg bg-slate-900/10 blur-xl"></div>
      
      {/* Book logo with scale animation */}
      <div className="relative w-24 h-24 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl flex items-center justify-center shadow-2xl animate-pulse" style={{ animationDuration: '2s' }}>
        <svg className="w-14 h-14 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        
        {/* Inner shimmer effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer rounded-xl"></div>
      </div>
      
      {/* Orbiting particles */}
      <div className="absolute inset-0 animate-spin" style={{ animationDuration: '4s', animationDirection: 'reverse' }}>
        <div className="absolute top-0 left-1/2 w-2 h-2 bg-slate-400 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute right-0 top-1/2 w-2 h-2 bg-slate-500 rounded-full translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute left-0 top-1/2 w-2 h-2 bg-slate-600 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
      </div>
    </div>
    
    <style>{`
      @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
      }
      .animate-shimmer {
        animation: shimmer 2s infinite;
      }
    `}</style>
  </div>
);

// Skip Navigation Component for Accessibility
const SkipNavigation = () => (
  <a
    href="#main-content"
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md"
  >
    Skip to main content
  </a>
);

function Router() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Switch>
        <Route path="/" component={Home} />
        <ProtectedRoute path="/upload" component={Upload} />
        <ProtectedRoute path="/find" component={FindNotes} />
        <ProtectedRoute path="/profile" component={Profile} />
        <ProtectedRoute path="/settings" component={Settings} />
        <ProtectedRoute path="/flagged" component={FlaggedContent} />
        <ProtectedRoute path="/analytics" component={Analytics} />
        <ProtectedRoute path="/leaderboard" component={LeaderboardPage} />
        <ProtectedRoute path="/admin" component={AdminPanel} />
        <Route path="/auth" component={AuthPage} />
        <Route path="/reset-password" component={ResetPassword} />
        <Route path="/cors-debug" component={CorsDebug} />
        <Route component={NotFound} />
      </Switch>
    </Suspense>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <SkipNavigation />
          <div className="min-h-screen flex flex-col">
            <Suspense fallback={<PageLoader />}>
              <Switch>
                <Route path="/auth">
                  <AuthPage />
                </Route>
                <Route path="/reset-password">
                  <ResetPassword />
                </Route>
                <Route>
                  <>
                    <Header />
                    <main id="main-content" className="flex-grow" tabIndex={-1}>
                      <Router />
                    </main>
                    <Footer />
                  </>
                </Route>
              </Switch>
              <ToastContainer />
              <NoteBuddy />
            </Suspense>
          </div>
          <Toaster />
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
