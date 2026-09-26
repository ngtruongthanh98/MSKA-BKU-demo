import React, { useEffect, useState } from 'react';
import DefaultLayout from '@/layouts/default';
import { listDemoVideos, getDemoResult, DemoVideoSummary, DemoResult } from '@/utils/api';

const CATEGORY_LABELS: Record<string, string> = {
  gtnc_warning: 'Caught by GTNC (numeral warning)',
  perfect_recognition: 'Perfect recognition',
  typical_errors: 'Typical partial errors',
};

const DemoPage: React.FC = () => {
  const [videos, setVideos] = useState<DemoVideoSummary[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [result, setResult] = useState<DemoResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    listDemoVideos()
      .then((data) => {
        setVideos(data);
        if (data.length > 0) setSelected(data[0].name);
      })
      .catch(() => setError('Could not load the demo video list. Is the backend running on port 3000?'));
  }, []);

  useEffect(() => {
    if (!selected) return;
    setLoading(true);
    setError('');
    getDemoResult(selected)
      .then(setResult)
      .catch(() => setError('Could not load this example.'))
      .finally(() => setLoading(false));
  }, [selected]);

  const grouped = videos.reduce<Record<string, DemoVideoSummary[]>>((acc, v) => {
    (acc[v.category] = acc[v.category] || []).push(v);
    return acc;
  }, {});

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center max-w-3xl gap-4 mx-auto">
        <h1 className="mb-2 text-3xl font-bold text-center">MSKA Replay Demo</h1>
        <p className="text-sm text-center text-default-500">
          Real MSKA-SLR/SLT outputs on PHOENIX-2014T test videos, replayed locally
          from the reproducibility analysis &mdash; no GPU or model server needed.
        </p>

        <select
          className="w-full p-3 mt-4 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {Object.entries(grouped).map(([category, items]) => (
            <optgroup key={category} label={CATEGORY_LABELS[category] || category}>
              {items.map((v) => (
                <option key={v.name} value={v.name}>
                  {v.name.replace(/^test\//, '')}
                </option>
              ))}
            </optgroup>
          ))}
        </select>

        {error && <div className="mt-2 text-red-600">{error}</div>}
        {loading && <div className="mt-2 text-blue-500">Loading...</div>}

        <div className="w-full p-6 mt-2 text-center border-2 border-dashed rounded-lg text-default-400 border-default-200">
          Video playback needs a local PHOENIX-2014T sample clip for this name under
          frontend/public/demo-media/ &mdash; the original hosted video/frame buckets are
          no longer publicly reachable. Showing recognized gloss and translation below.
        </div>

        {result && (
          <div className="w-full p-6 mt-2 bg-gray-100 rounded-lg shadow-md dark:bg-gray-800">
            {result.gtncFlag ? (
              <div className="p-4 mb-4 text-amber-900 bg-amber-100 border border-amber-300 rounded-lg dark:bg-amber-900/30 dark:text-amber-200 dark:border-amber-700">
                <strong>&#9888; GTNC warning:</strong> the recognized glosses and the
                translated numbers disagree &mdash; double-check the numbers in this
                video before trusting the translation.
              </div>
            ) : (
              <div className="p-4 mb-4 text-green-900 bg-green-100 border border-green-300 rounded-lg dark:bg-green-900/30 dark:text-green-200 dark:border-green-700">
                No numeral inconsistency detected.
              </div>
            )}

            <div>
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Recognized glosses (MSKA-SLR)
              </h3>
              <p className="mt-1 font-mono text-gray-600 dark:text-gray-400">{result.glossHyp || '(empty)'}</p>
            </div>

            <div className="mt-4">
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                German translation (MSKA-SLT)
              </h3>
              <p className="mt-1 text-gray-600 dark:text-gray-400">{result.textHyp}</p>
            </div>

            <div className="mt-4 text-sm text-default-500">
              <p>Reference gloss: <span className="font-mono">{result.glossRef}</span></p>
              <p>Reference text: {result.textRef}</p>
            </div>
          </div>
        )}
      </section>
    </DefaultLayout>
  );
};

export default DemoPage;
