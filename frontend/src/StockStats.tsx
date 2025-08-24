import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Product {
  id: number;
  name: string;
  brand: string;
  stock: number;
  buying_price: string;
  selling_price: string;
}

// Generate a palette of distinct colors
const COLORS = [
  '#1976d2', '#388e3c', '#fbc02d', '#d32f2f', '#7b1fa2', '#0288d1', '#c2185b',
  '#ffa000', '#388e3c', '#f57c00', '#455a64', '#0097a7', '#8bc34a', '#f44336',
  '#5d4037', '#cddc39', '#607d8b', '#e91e63', '#00bcd4', '#ff5722'
];

const getBarColors = (count: number) => {
  // Repeat colors if products > COLORS.length, but always unique for first N
  let colors = [];
  for (let i = 0; i < count; i++) {
    colors.push(COLORS[i % COLORS.length]);
  }
  return colors;
};

const StockStats: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('https://e-accoutant.onrender.com/api/products/');
      setProducts(response.data);
    } catch (err) {
      setError('Failed to fetch stock data');
    }
    setLoading(false);
  };

  const barColors = getBarColors(products.length);

  const chartData = {
    labels: products.map(product => `${product.name} (${product.brand})`),
    datasets: [
      {
        label: 'Stock Level',
        data: products.map(product => product.stock),
        backgroundColor: barColors,
        borderColor: barColors,
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Product Stock Levels',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Stock Quantity',
        },
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
  };

  return (
    <div className="stock-stats-container">
      <div className="stock-stats-header">
        <h2>Stock Statistics</h2>
        <button onClick={fetchProducts} className="refresh-btn">
          Refresh Data
        </button>
      </div>
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}
      {products.length > 0 ? (
        <div className="chart-container">
          <Bar data={chartData} options={options} />
        </div>
      ) : !loading && (
        <div className="no-data">No products found</div>
      )}
    </div>
  );
};

export default StockStats;