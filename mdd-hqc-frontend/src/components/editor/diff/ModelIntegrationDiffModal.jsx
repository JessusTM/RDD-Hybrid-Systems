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

/**
 * Visual scaffold for the future model-integration workflow.
 */
const ModelIntegrationDiffModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/75 p-3 backdrop-blur-sm sm:p-4">
      <div className="flex max-h-[92vh] w-full max-w-6xl flex-col overflow-hidden rounded-xl border border-ctp-surface1 bg-ctp-mantle shadow-2xl">
        <header className="flex flex-col items-stretch justify-between gap-4 border-b border-ctp-surface1 bg-ctp-crust px-4 py-4 sm:px-6 lg:flex-row lg:items-center">
          <div className="flex items-center gap-3 sm:gap-4">
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

          <div className="grid w-full grid-cols-2 items-stretch gap-3 lg:w-auto lg:grid-cols-[10rem_10rem_11.5rem_3.5rem]">
            <div className="flex h-14 w-full flex-col justify-center rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-4">
              <p className="text-[10px] font-bold uppercase leading-none text-ctp-subtext0">
                Status
              </p>
              <p className="mt-1.5 text-sm font-bold leading-none text-ctp-yellow">Pending</p>
            </div>

            <div className="flex h-14 w-full flex-col justify-center rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-4">
              <p className="whitespace-nowrap text-[10px] font-bold uppercase leading-none text-ctp-subtext0">
                Integration Progress
              </p>
              <p className="mt-1.5 text-sm font-bold leading-none text-ctp-text">
                <span className="text-ctp-mauve">0</span> / 3
              </p>
            </div>

            <button
              type="button"
              disabled
              title="Model integration will be implemented in a future phase"
              className="h-14 w-full cursor-not-allowed rounded-lg bg-ctp-surface1 px-5 text-sm font-bold uppercase text-ctp-overlay0 opacity-60"
            >
              Integrate Model
            </button>

            <button
              type="button"
              onClick={onClose}
              aria-label="Close model integration"
              title="Cancel model integration"
              className="flex h-14 w-14 justify-self-end items-center justify-center rounded-lg border border-ctp-red/50 bg-ctp-red/15 text-ctp-red transition-colors hover:bg-ctp-red hover:text-ctp-base lg:w-full"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </header>

        <main className="grid min-h-0 flex-1 overflow-auto lg:grid-cols-2 lg:overflow-hidden">
          <section className="flex min-h-[420px] min-w-0 flex-col border-b border-ctp-surface1 lg:border-b-0 lg:border-r">
            <div className="border-b border-ctp-surface1 bg-ctp-crust/60 px-4 py-2">
              <h3 className="text-xs font-bold uppercase tracking-wide text-ctp-subtext0">
                1. Proposed Changes
              </h3>
            </div>

            <div className="flex min-h-0 flex-1 bg-ctp-mantle p-4">
              <div className="flex h-full min-h-0 w-full flex-col overflow-hidden rounded-lg border-l-4 border-ctp-green bg-ctp-surface0/70">
                <div className="flex items-center justify-between border-b border-ctp-surface1 px-4 py-3">
                  <span className="text-xs font-bold text-ctp-green">
                    RESTAPIBasedIntegration
                  </span>

                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="rounded-md bg-ctp-green p-1.5 text-ctp-base"
                      title="Accept recommendation (visual prototype)"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      className="rounded-md bg-ctp-red p-1.5 text-ctp-base"
                      title="Reject recommendation (visual prototype)"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <pre className="themed-scrollbar min-h-0 flex-1 overflow-auto whitespace-pre-wrap p-4 font-mono text-[13px] leading-5 text-ctp-text">
                  {proposedChanges}
                </pre>
              </div>
            </div>
          </section>

          <section className="flex min-h-[420px] min-w-0 flex-col">
            <div className="border-b border-ctp-surface1 bg-ctp-crust/60 px-4 py-2">
              <h3 className="text-xs font-bold uppercase tracking-wide text-ctp-subtext0">
                2. Final UVL Model
              </h3>
            </div>

            <div className="flex min-h-0 flex-1 bg-ctp-mantle p-4">
              <pre className="themed-scrollbar h-full min-h-0 w-full overflow-auto whitespace-pre-wrap rounded-lg bg-ctp-base p-4 font-mono text-[13px] leading-5 text-ctp-text">
                {finalUvlModel}
              </pre>
            </div>
          </section>
        </main>

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-ctp-surface1 bg-ctp-crust px-4 py-3">
          <div className="flex flex-wrap gap-4 text-xs sm:gap-6">
            <span className="text-ctp-green">Pending proposals</span>
            <span className="text-ctp-mauve">Integrated blocks</span>
          </div>

          <p className="text-xs italic text-ctp-subtext0">
            Visual scaffold for the future model-integration workflow.
          </p>
        </footer>
      </div>
    </div>
  )
}

export default ModelIntegrationDiffModal
