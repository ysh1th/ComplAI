"use client";

import { AnimatePresence } from "framer-motion";
import type { UserWithState } from "@/lib/types";
import { UserCard } from "./UserCard";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Users } from "lucide-react";

interface UserRosterProps {
  users: UserWithState[];
  selectedUserId: string | null;
  onSelectUser: (userId: string) => void;
  loading: boolean;
  recentlyUpdatedId?: string | null;
}

export function UserRoster({
  users,
  selectedUserId,
  onSelectUser,
  loading,
  recentlyUpdatedId,
}: UserRosterProps) {
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingSpinner text="Loading users..." />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-deriv-dark-border">
        <div className="flex items-center gap-2">
          <Users className="w-5 h-5 text-deriv-red" />
          <h2 className="text-base font-bold text-white">User Roster</h2>
          <span className="text-xs text-deriv-grey ml-auto">
            {users.length} users
          </span>
        </div>
      </div>

      {/* User list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        <AnimatePresence>
          {users.map((user) => (
            <UserCard
              key={user.profile.user_id}
              user={user}
              selected={selectedUserId === user.profile.user_id}
              isNew={recentlyUpdatedId === user.profile.user_id}
              onClick={() => onSelectUser(user.profile.user_id)}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
