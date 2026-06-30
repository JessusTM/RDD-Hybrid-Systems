import { Check, GitCompare, X } from "lucide-react"

const proposedChanges = `features
  Functionality
    mandatory
      actor: ChileEsPres
      PerformDelivery
        {
          kind "goal"
          fastDelivery "true"
          optimalResourceUsage "true"
        }

      actor: Route Planning System
      GenerateRoutePlan
        {
          kind "task"
        }

Algorithm
  Quantum
    mandatory
      actor: Quantum Module
      ExecuteQuantumAnnealingAlgorithm

RESTAPIBasedIntegration
  mandatory
    {
      kind "implementation"
      provider "REST API-based integration"
    }

PythonDWaveOceanSDK
  mandatory
    {
      kind "implementation"
      provider "Python + D-Wave Ocean SDK"
    }`

const finalUvlModel = `features
  Functionality
    mandatory
      actor: ChileEsPres
      PerformDelivery
        {
          kind "goal"
          fastDelivery "true"
          optimalResourceUsage "true"
        }

      actor: Route Planning System
      GenerateRoutePlan
        {
          kind "task"
        }

      mandatory
        actor: Route Planning System
        NationalMap
          {
            kind "resource"
          }

      actor: Route Planning System
      VehicleFleet
        {
          kind "resource"
        }

      actor: Route Planning System
      CurrentDemand
        {
          kind "resource"
        }`

const ModelIntegrationDiffModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
      <div className="flex max-h-[90vh] w-full max-w-6xl flex-col overflow-hidden rounded-xl border border-ctp-surface1 bg-ctp-mantle shadow-2xl">
        <header className="flex items-center justify-between border-b border-ctp-surface1 bg-ctp-crust px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="rounded-lg bg-ctp-mauve/20 p-3 text-ctp-mauve">
              <GitCompare className="h-6 w-6" />
            </div>

            <div>
              <h2 className="text-lg font-bold uppercase tracking-wide text-ctp-text">
                Model Integration
              </h2>
              <p className="text-sm text-ctp-subtext0">
                Map design decisions to the UVL structure
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-5 py-2">
              <p className="text-[10px] font-bold uppercase text-ctp-subtext0">
                Status
              </p>
              <p className="text-xs font-bold text-ctp-yellow">● Pending</p>
            </div>

            <div className="rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-5 py-2">
              <p className="text-[10px] font-bold uppercase text-ctp-subtext0">
                Integration Progress
              </p>
              <p className="text-base font-bold text-ctp-text">
                <span className="text-ctp-mauve">0</span> / 3
              </p>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-semibold text-ctp-text hover:bg-ctp-surface0"
            >
              Cancel
            </button>

            <button
              type="button"
              disabled
              className="cursor-not-allowed rounded-lg bg-ctp-surface1 px-5 py-2 text-sm font-bold uppercase text-ctp-overlay0 opacity-60"
            >
              Integrate Model
            </button>
          </div>
        </header>

        <main className="grid min-h-[540px] flex-1 overflow-hidden lg:grid-cols-2">
          <section className="flex min-w-0 flex-col border-r border-ctp-surface1">
            <div className="border-b border-ctp-surface1 bg-ctp-crust/60 px-4 py-2">
              <h3 className="text-xs font-bold uppercase tracking-wide text-ctp-subtext0">
                1. Proposed Changes
              </h3>
            </div>

            <div className="flex-1 overflow-auto bg-ctp-mantle p-4">
              <div className="mb-4 rounded-lg border-l-4 border-ctp-green bg-ctp-surface0/70">
                <div className="flex items-center justify-between border-b border-ctp-surface1 px-4 py-3">
                  <span className="text-xs font-bold text-ctp-green">
                    RESTAPIBasedIntegration
                  </span>

                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="rounded bg-ctp-green p-1 text-ctp-base"
                      title="Accept recommendation"
                    >
                      <Check className="h-3 w-3" />
                    </button>

                    <button
                      type="button"
                      className="rounded bg-ctp-red p-1 text-ctp-base"
                      title="Reject recommendation"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                </div>

                <pre className="whitespace-pre-wrap p-4 font-mono text-[11px] leading-5 text-ctp-text">
                  {proposedChanges}
                </pre>
              </div>
            </div>
          </section>

          <section className="flex min-w-0 flex-col">
            <div className="border-b border-ctp-surface1 bg-ctp-crust/60 px-4 py-2">
              <h3 className="text-xs font-bold uppercase tracking-wide text-ctp-subtext0">
                2. Final UVL Model
              </h3>
            </div>

            <div className="flex-1 overflow-auto bg-ctp-mantle p-4">
              <pre className="min-h-full whitespace-pre-wrap rounded-lg bg-ctp-base p-4 font-mono text-[11px] leading-5 text-ctp-text">
                {finalUvlModel}
              </pre>
            </div>
          </section>
        </main>

        <footer className="flex items-center justify-between border-t border-ctp-surface1 bg-ctp-crust px-5 py-3">
          <div className="flex gap-6 text-xs">
            <span className="text-ctp-green">■ Pending proposals</span>
            <span className="text-ctp-mauve">■ Integrated blocks</span>
          </div>

          <p className="text-xs italic text-ctp-subtext0">
            Click features in the model to move suggested blocks.
          </p>
        </footer>
      </div>
    </div>
  )
}

export default ModelIntegrationDiffModal