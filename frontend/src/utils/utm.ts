// Simple UTM capture and storage utility

export type UtmAttribution = {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  referrer_url?: string;
  landing_page_url?: string;
  gclid?: string;
  fbclid?: string;
};

const STORAGE_KEY = 'lead_utm_attribution';

export function parseQuery(search: string): Record<string, string> {
  const params = new URLSearchParams(search.startsWith('?') ? search : `?${search}`);
  const result: Record<string, string> = {};
  params.forEach((value, key) => {
    result[key] = value;
  });
  return result;
}

export function captureUtmAttribution(currentUrl: string, referrer: string): UtmAttribution | null {
  try {
    const url = new URL(currentUrl);
    const q = parseQuery(url.search);
    const attribution: UtmAttribution = {
      utm_source: q['utm_source'] || undefined,
      utm_medium: q['utm_medium'] || undefined,
      utm_campaign: q['utm_campaign'] || undefined,
      utm_term: q['utm_term'] || undefined,
      utm_content: q['utm_content'] || undefined,
      referrer_url: referrer || undefined,
      landing_page_url: url.origin + url.pathname + (url.search || ''),
      gclid: q['gclid'] || undefined,
      fbclid: q['fbclid'] || undefined,
    };

    // Only persist if any useful field exists
    const hasField = Object.values(attribution).some((v) => typeof v === 'string' && v.length > 0);
    if (hasField) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(attribution));
      return attribution;
    }
    return null;
  } catch {
    return null;
  }
}

export function getStoredUtmAttribution(): UtmAttribution | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as UtmAttribution;
  } catch {
    return null;
  }
}

export function clearUtmAttribution(): void {
  localStorage.removeItem(STORAGE_KEY);
}


