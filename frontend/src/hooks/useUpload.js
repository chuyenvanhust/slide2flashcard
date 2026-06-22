// hooks/useUpload.js — Upload PDF + poll job status

import { useState, useRef } from "react";
import { api } from "../api/client";

export function useUpload(deckId = null) {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [polling, setPolling] = useState(false);
  const intervalRef = useRef(null);

  const upload = async (file) => {
    const { job_id } = await api.uploadPDF(file, deckId);
    setJobId(job_id);
    setPolling(true);

    intervalRef.current = setInterval(async () => {
      const s = await api.getJobStatus(job_id);
      setStatus(s);
      if (s.status === "done" || s.status === "failed") {
        clearInterval(intervalRef.current);
        setPolling(false);
      }
    }, 1000);
  };

  const reset = () => {
    clearInterval(intervalRef.current);
    setJobId(null);
    setStatus(null);
    setPolling(false);
  };

  const isDone = status?.status === "done";
  const isFailed = status?.status === "failed";

  return { upload, status, polling, isDone, isFailed, reset };
}
