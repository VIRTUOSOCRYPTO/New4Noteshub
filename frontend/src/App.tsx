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
const Header = lazy(() => import("@/components/layout/Header"));
const Footer = lazy(() => import("@/components/layout/Footer"));
const ToastContainer = lazy(() => import("@/components/ui/toast-container"));
const NoteBuddy = lazy(() => import("@/components/NoteBuddy"));

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
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
