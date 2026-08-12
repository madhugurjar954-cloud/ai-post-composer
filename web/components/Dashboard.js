import React from 'react'

export default function Dashboard(){
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="grid md:grid-cols-2 gap-6">
        <section>
          <h2 className="text-xl font-semibold mb-3">Subscriptions</h2>
          <div className="border rounded p-3 bg-slate-50">
            <p className="text-sm text-slate-600">No subscriptions yet — this is a scaffold. Use the API to add items or wait for the UI forms (next commits).</p>
          </div>
        </section>
        <section>
          <h2 className="text-xl font-semibold mb-3">Medications</h2>
          <div className="border rounded p-3 bg-slate-50">
            <p className="text-sm text-slate-600">No medications yet — this is a scaffold. Add meds with schedule and export ICS/QR next.</p>
          </div>
        </section>
      </div>
      <div className="mt-6">
        <h3 className="font-semibold">Next steps</h3>
        <ol className="list-decimal list-inside text-sm text-slate-600">
          <li>Implement add/edit forms for subscriptions and medications.</li>
          <li>Implement ICS export and QR generation endpoints.</li>
          <li>Add AI parsing endpoint and scheduling worker (SendGrid/GitHub Actions).</li>
        </ol>
      </div>
    </div>
  )
}
