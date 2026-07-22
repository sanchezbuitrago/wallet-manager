import { Route, Switch, Redirect } from "wouter";
import { useAuth } from "./ui/hooks/useAuth";
import { Layout } from "./ui/components/Layout";
import { LoginPage } from "./ui/pages/LoginPage";
import { RegisterPage } from "./ui/pages/RegisterPage";
import { VerifyPage } from "./ui/pages/VerifyPage";
import { RecoverPinPage } from "./ui/pages/RecoverPinPage";
import { DashboardPage } from "./ui/pages/DashboardPage";
import { MovementsPage } from "./ui/pages/MovementsPage";
import { MovementDetailPage } from "./ui/pages/MovementDetailPage";
import { SettingsPage } from "./ui/pages/SettingsPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Redirect to="/login" />;
  return <Layout>{children}</Layout>;
}

export function App() {
  return (
    <Switch>
      <Route path="/login" component={LoginPage} />
      <Route path="/register" component={RegisterPage} />
      <Route path="/verify" component={VerifyPage} />
      <Route path="/recover-pin" component={RecoverPinPage} />

      <Route path="/">
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      </Route>

      <Route path="/movements">
        <ProtectedRoute>
          <MovementsPage />
        </ProtectedRoute>
      </Route>

      <Route path="/movements/:id">
        {(params) => (
          <ProtectedRoute>
            <MovementDetailPage id={params.id} />
          </ProtectedRoute>
        )}
      </Route>

      <Route path="/settings">
        <ProtectedRoute>
          <SettingsPage />
        </ProtectedRoute>
      </Route>

      <Route>
        <Redirect to="/login" />
      </Route>
    </Switch>
  );
}
