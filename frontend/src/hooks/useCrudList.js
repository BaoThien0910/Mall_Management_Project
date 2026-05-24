import { useCallback, useEffect, useState } from "react";
import { showApiError } from "../services/apiClient";
import { toArray } from "../utils/data";

export function useCrudList(fetcher, initialParams = {}) {
  const [params, setParams] = useState(initialParams);
  const [payload, setPayload] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (nextParams = params) => {
    setLoading(true);
    try {
      const data = await fetcher(nextParams);
      setPayload(data);
      setItems(toArray(data));
    } catch (error) {
      showApiError(error);
    } finally {
      setLoading(false);
    }
  }, [fetcher, params]);

  useEffect(() => { load(params); }, []);

  const updateParams = (nextParams) => {
    setParams(nextParams);
    load(nextParams);
  };

  return { items, payload, loading, params, setParams: updateParams, reload: () => load(params) };
}
