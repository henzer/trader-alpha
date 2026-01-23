import PatternCanvas from '@/components/PatternCanvas';

export default function DrawPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Pattern Drawing</h1>
          <p className="text-gray-400">
            Draw a price pattern and find stocks that match this shape
          </p>
        </div>

        <PatternCanvas />
      </div>
    </div>
  );
}