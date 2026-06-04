import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { searchStocks } from "../lib/api";
import type { StockOption } from "../types/analysis";

interface StockSearchProps {
  value: string;
  onSelect: (stock: StockOption) => void;
}

export function StockSearch({ value, onSelect }: StockSearchProps) {
  const [query, setQuery] = useState(value);
  const [items, setItems] = useState<StockOption[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    setQuery(value);
  }, [value]);

  async function handleSearch() {
    setError("");
    try {
      setItems(await searchStocks(query));
    } catch (err) {
      setError(err instanceof Error ? err.message : "股票搜索失败");
    }
  }

  return (
    <div className="stock-search">
      <label>
        股票搜索
        <div className="inline-control">
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="代码或名称" />
          <button type="button" onClick={handleSearch} title="搜索股票">
            <Search size={16} aria-hidden="true" />
          </button>
        </div>
      </label>
      {items.length > 0 ? (
        <div className="stock-results" aria-label="股票搜索结果">
          {items.map((item) => (
            <button type="button" key={item.symbol} onClick={() => onSelect(item)}>
              <span>{item.symbol}</span>
              <strong>{item.name}</strong>
              <small>{item.market}</small>
            </button>
          ))}
        </div>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
    </div>
  );
}
