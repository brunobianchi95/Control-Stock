import { useEffect, useState } from "react";
const url = "http://localhost:5000/api/sellHistory";

type Venta = {
  cantidad: string;
  cient_id: number;
  email: string;
  fecha: string;
  precio_v: string;
  vendedor: string;
  vendedor_id: number;
  venta_id: number;
};

const Ventas = () => {
  const [ventas, setVentas] = useState<Array<Venta>>([]);
  const fetchSellHistory = async () => {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
    });

    const json = await response.json();
    setVentas(json);
  };

  useEffect(() => {
    fetchSellHistory();
  }, []);

  return (
    <div>
      <h2>Ventas</h2>
      <ul>
        {ventas.map((venta) => (
          <li key={venta.venta_id}>
            <h4>Vendedor: {venta.vendedor}</h4>
            <h4>Cantidad: {venta.cantidad}</h4>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Ventas;
