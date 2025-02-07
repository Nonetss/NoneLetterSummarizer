import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./DaysList.css"; // Importa el CSS

const API_URL = import.meta.env.VITE_API_URL;

function DaysList() {
  const [days, setDays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState("dark");

  // Obtener la lista de días desde el backend
  const fetchDays = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/days`);
      if (!res.ok) {
        throw new Error("Error al obtener los días");
      }
      const data = await res.json();
      setDays(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  // Refrescar newsletters llamando al endpoint GET /api/v1/newsletter/
  const refreshNewsletters = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/newsletter/`);
      if (!res.ok) throw new Error("Error al refrescar newsletters");
      await res.json();
      fetchDays();
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  // Generar resumen general del día
  const regenerateDaySummary = async (dayId) => {
    try {
      const res = await fetch(`${API_URL}/api/v1/days/${dayId}/summarize`, {
        method: "POST",
      });
      if (!res.ok)
        throw new Error("Error al generar el resumen general del día");
      const updatedDay = await res.json();
      setDays((prevDays) =>
        prevDays.map((day) =>
          day.id === dayId ? { ...day, summary: updatedDay.summary } : day,
        ),
      );
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  // Toggle para cambiar de tema
  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  useEffect(() => {
    fetchDays();
  }, []);

  if (loading) return <p>Cargando días...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className={`container ${theme}`}>
      <header className="header">
        <h1>Resumen de Newsletters por Día</h1>
        <div className="header-buttons">
          <button className="theme-toggle" onClick={toggleTheme}>
            Cambiar a {theme === "light" ? "oscuro" : "claro"}
          </button>
          <button className="refresh" onClick={refreshNewsletters}>
            Refrescar newsletters
          </button>
        </div>
      </header>

      {days.map((day) => (
        <div key={day.id} className="day-card">
          <h2>
            {new Date(day.fecha).toLocaleDateString("es-ES", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </h2>

          {/* Resumen general del día con la lista de newsletters recibidas */}
          <details className="day-summary">
            <summary>📅 Resumen general del día</summary>
            <div className="summary-content">
              <ReactMarkdown>
                {day.summary ? day.summary : "No generado"}
              </ReactMarkdown>

              <h4>📭 Newsletters recibidas:</h4>
              <ul>
                {day.newsletters.map((newsletter) => (
                  <li key={newsletter.id}>
                    <strong>{newsletter.subject}</strong> - Recibida el{" "}
                    {new Date(newsletter.received_at).toLocaleTimeString(
                      "es-ES",
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </details>

          <button
            className="generate-summary"
            onClick={() => regenerateDaySummary(day.id)}
          >
            📝 Generar resumen general
          </button>

          {/* Desplegable para ver las newsletters del día */}
          <details className="newsletters-details">
            <summary>📬 Ver newsletters de este día</summary>
            <div className="newsletters-list">
              {day.newsletters.map((newsletter) => (
                <div key={newsletter.id} className="newsletter-card">
                  <h3>{newsletter.subject}</h3>
                  <p>
                    <strong>Autor:</strong> {newsletter.author}
                  </p>
                  <div>
                    <strong>📌 Resumen de la newsletter:</strong>
                    <ReactMarkdown>
                      {newsletter.summary
                        ? newsletter.summary
                        : "No disponible"}
                    </ReactMarkdown>
                  </div>
                  <p>
                    <small>
                      Recibida:{" "}
                      {new Date(newsletter.received_at).toLocaleString("es-ES")}
                    </small>
                  </p>
                </div>
              ))}
            </div>
          </details>
        </div>
      ))}
    </div>
  );
}

export default DaysList;
