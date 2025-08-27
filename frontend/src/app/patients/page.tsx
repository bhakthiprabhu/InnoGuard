"use client";

import { useEffect, useState, useMemo } from "react";
import Image from "next/image";
import * as Tooltip from "@radix-ui/react-tooltip";
import { Download, Users, Activity, HeartPulse } from "lucide-react";

interface Patient {
  name?: string;
  phone?: string;
  email?: string;
  address?: string;
  patient_id?: string;
  location?: string;
  age: number;
  disease: string;
  purchase_amount: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [role, setRole] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 10;

  const fetchPatients = async (page: number) => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    setRole(role);

    if (!token) return;

    const offset = page * limit;
    const res = await fetch(
      `${API_URL}/patients?limit=${limit}&offset=${offset}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    const data = await res.json();

    if (data && Array.isArray(data.data)) {
      if (Array.isArray(data.data[0])) {
        // ✅ Explicitly map rows into Patient objects
        const transformed: Patient[] = data.data.map((row: unknown[]) => ({
          patient_id: String(row[0] ?? ""),
          location: String(row[1] ?? ""),
          age: Number(row[2] ?? 0),
          disease: String(row[3] ?? ""),
          purchase_amount: Number(row[4] ?? 0),
        }));

        setPatients(transformed);
      } else {
        setPatients(data.data as Patient[]);
      }

      if (data.pagination?.total) {
        setTotal(data.pagination.total);
      }
    }
  };

  useEffect(() => {
    fetchPatients(page);
  }, [page]);

  const handleDownload = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const res = await fetch(`${API_URL}/download/patients`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      alert("Failed to download");
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "patients.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  // 📊 Dashboard stats
  const stats = useMemo(() => {
    const totalPatients = total || patients.length;
    const avgAge =
      patients.length > 0
        ? Math.round(
            patients.reduce((sum, p) => sum + (p.age || 0), 0) / patients.length
          )
        : 0;

    const topDisease =
      patients.length > 0
        ? patients.reduce<Record<string, number>>((acc, p) => {
            acc[p.disease] = (acc[p.disease] || 0) + 1;
            return acc;
          }, {})
        : {};

    const mostCommonDisease =
      Object.keys(topDisease).length > 0
        ? Object.entries(topDisease).sort((a, b) => b[1] - a[1])[0][0]
        : "N/A";

    return { totalPatients, avgAge, mostCommonDisease };
  }, [patients, total]);

  return (
    <main className="p-6 space-y-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <header className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Image
            src="/logo.png"
            alt="InnoGuard Logo"
            width={40}
            height={40}
            className="rounded-lg shadow"
          />
          <div>
            <h1 className="text-2xl font-bold text-blue-700">InnoGuard</h1>
            <p className="text-xs text-gray-500">
              The Smart Security Guard for Sensitive Data
            </p>
            {role && (
              <span className="inline-block mt-1 text-xs font-medium text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">
                Role: {role}
              </span>
            )}
          </div>
        </div>

        <Tooltip.Provider>
          <Tooltip.Root>
            <Tooltip.Trigger asChild>
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700"
              >
                <Download className="w-4 h-4" /> CSV
              </button>
            </Tooltip.Trigger>
            <Tooltip.Content
              side="bottom"
              className="bg-gray-800 text-white px-2 py-1 rounded-md text-sm"
            >
              Download patient data
            </Tooltip.Content>
          </Tooltip.Root>
        </Tooltip.Provider>
      </header>

      {/* 📊 Stats */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="flex items-center gap-3 p-4 bg-white shadow rounded-lg">
          <Users className="w-8 h-8 text-blue-600" />
          <div>
            <p className="text-sm text-gray-500">Total Patients</p>
            <h3 className="text-lg font-bold">{stats.totalPatients}</h3>
          </div>
        </div>
        <div className="flex items-center gap-3 p-4 bg-white shadow rounded-lg">
          <Activity className="w-8 h-8 text-green-600" />
          <div>
            <p className="text-sm text-gray-500">Average Age</p>
            <h3 className="text-lg font-bold">{stats.avgAge}</h3>
          </div>
        </div>
        <div className="flex items-center gap-3 p-4 bg-white shadow rounded-lg">
          <HeartPulse className="w-8 h-8 text-red-600" />
          <div>
            <p className="text-sm text-gray-500">Top Disease</p>
            <h3 className="text-lg font-bold">{stats.mostCommonDisease}</h3>
          </div>
        </div>
      </section>

      {/* 📋 Patient Table */}
      <div className="overflow-x-auto rounded-lg border shadow-sm">
        <table className="min-w-full text-sm border-collapse">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              {patients.length > 0 &&
                Object.keys(patients[0]).map((key) => (
                  <th
                    key={key}
                    className="px-4 py-2 border font-medium text-gray-700"
                  >
                    {key}
                  </th>
                ))}
            </tr>
          </thead>
          <tbody>
            {patients.map((p, i) => (
              <tr
                key={i}
                className="border-t odd:bg-white even:bg-gray-50 hover:bg-blue-50 transition"
              >
                {Object.values(p).map((val, idx) => (
                  <td key={idx} className="px-4 py-2 border">
                    {String(val)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-6">
        <button
          onClick={() => setPage((p) => Math.max(p - 1, 0))}
          disabled={page === 0}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          ◀ Previous
        </button>

        <span className="text-gray-600">
          Page <b>{page + 1}</b> of {Math.ceil(total / limit) || 1}
        </span>

        <button
          onClick={() =>
            setPage((p) => ((p + 1) * limit < total ? p + 1 : p))
          }
          disabled={(page + 1) * limit >= total}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Next ▶
        </button>
      </div>
    </main>
  );
}
