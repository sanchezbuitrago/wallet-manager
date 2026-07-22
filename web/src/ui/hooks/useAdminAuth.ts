import { useSyncExternalStore, useEffect, useState } from "react";
import { useLocation } from "wouter";
import { authStore } from "../../core/stores/auth.store";
import { api } from "../../core/api/client";
import type { UserProfile } from "../../core/types";

export function useAdminAuth() {
  const [, setLocation] = useLocation();
  const isAuthenticated = useSyncExternalStore(
    authStore.subscribe,
    authStore.isAuthenticated,
    authStore.isAuthenticated,
  );
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    api
      .get<UserProfile>("/users/myself")
      .then((res) => {
        if (res.success && res.body.is_admin) {
          setIsAdmin(true);
          setProfile(res.body);
        } else {
          setIsAdmin(false);
        }
        setLoading(false);
      })
      .catch(() => {
        setIsAdmin(false);
        setLoading(false);
      });
  }, [isAuthenticated]);

  useEffect(() => {
    if (!loading && isAuthenticated && isAdmin === false) {
      setLocation("/");
    }
  }, [loading, isAuthenticated, isAdmin, setLocation]);

  return { isAuthenticated, isAdmin, profile, loading };
}
