"use client";

import { useState } from "react";
import { Info } from "lucide-react";

import Header from "@/src/components/Header";
import Footer from "@/src/components/Footer";
import HealthBot from "@/src/components/HealthBot";

export default function Home() {
  const [newTopicKey, setNewTopicKey] =
    useState(0);

  function handleNewTopic() {
    setNewTopicKey(
      (current) => current + 1
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f9fc]">
      <Header
        onNewTopic={handleNewTopic}
      />

      <HealthBot key={newTopicKey} />

      <div className="border-t border-slate-200/60 bg-white/50">
        <div className="mx-auto flex max-w-6xl items-center justify-center gap-2 px-6 py-3 text-center text-[11px] text-slate-400">
          <Info size={13} />

          HealthBot is an educational assistant and
          should not be used for diagnosis or emergency
          medical decisions.
        </div>
      </div>

      <Footer />
    </div>
  );
}