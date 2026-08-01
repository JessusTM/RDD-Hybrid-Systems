/**
 * Sidebar components that expose predefined XML examples for the frontend flow.
 */

import { BookOpen, ChevronRight, Lightbulb, X } from "lucide-react"

const examples = [
  {
    id: "chileespres",
    name: "ChileEsPres",
    description:
      "Enterprise route-planning scenario with a quantum annealing module for improved delivery routes.",
    url: "/examples/ChileEsPres.xml",
    previewImage: "/images/ChileEsPres.svg",
    previewAlt: "ChileEsPres iStar model overview",
    tags: [
      ["i* 2.0", "border-ctp-mauve/30 bg-ctp-mauve/10 text-ctp-mauve"],
      ["CIM", "border-ctp-blue/30 bg-ctp-blue/10 text-ctp-blue"],
      ["Transport", "border-ctp-green/30 bg-ctp-green/10 text-ctp-green"],
      ["Logistics", "border-ctp-yellow/30 bg-ctp-yellow/10 text-ctp-yellow"],
    ],
  },
  {
    id: "q-tradex",
    name: "Q-TradeX",
    description:
      "Hybrid BTC classification using classical models and a VQC on IBM Quantum.",
    url: "/examples/Q-TradeX.xml",
    previewImage: "/images/Q-TradeX.svg",
    previewAlt: "Q-TradeX iStar model overview",
    tags: [
      ["i* 2.0", "border-ctp-mauve/30 bg-ctp-mauve/10 text-ctp-mauve"],
      ["CIM", "border-ctp-blue/30 bg-ctp-blue/10 text-ctp-blue"],
      ["Finance", "border-ctp-green/30 bg-ctp-green/10 text-ctp-green"],
      ["QML", "border-ctp-yellow/30 bg-ctp-yellow/10 text-ctp-yellow"],
    ],
  },
]

/**
 * Displays the example catalog used to start the flow from a predefined CIM model.
 *
 * This component is used by the main application so users can test the transformation
 * pipeline quickly without preparing their own upload first.
 */
export const ExamplesSidebar = ({ isOpen, onClose, onSelectExample }) => {
  /**
   * Selects the built-in example and closes the sidebar afterwards.
   *
   * This handler is used by the example card because the sidebar is responsible for
   * packaging the predefined example metadata before the app consumes it.
   */
  const handleSelect = (example) => {
    onSelectExample?.(example)
    onClose?.()
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className={[
          "fixed inset-0 z-[60] bg-ctp-base/70 backdrop-blur-sm transition-opacity duration-300",
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none",
        ].join(" ")}
        onClick={onClose}
      />

      {/* Sidebar panel */}
        <aside
          className={[
          "fixed left-0 top-0 z-[70] h-full w-full max-w-[540px] border-r border-ctp-surface1 bg-ctp-mantle shadow-2xl transition-transform duration-300",
          isOpen ? "translate-x-0" : "-translate-x-full",
        ].join(" ")}
      >
          {/* Sidebar content */}
          <div className="flex h-full flex-col">
            {/* Sidebar header */}
            <div className="flex items-center justify-between border-b border-ctp-surface1 px-6 py-6">
             <div className="flex items-center gap-4">
               <div className="rounded-xl bg-ctp-surface0 p-3">
                 <BookOpen className="h-6 w-6 text-ctp-mauve" />
               </div>
               <div>
                 <h2 className="text-3xl font-bold leading-none text-ctp-text">Examples</h2>
               </div>
             </div>

             <button
               type="button"
               onClick={onClose}
               className="flex h-12 w-12 items-center justify-center rounded-xl text-[#a0988c] transition-colors hover:bg-ctp-surface0 hover:text-ctp-text"
               aria-label="Close examples"
             >
               <X className="h-6 w-6" />
             </button>
          </div>

          {/* Example list */}
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="mb-6 rounded-2xl border border-ctp-blue/20 bg-ctp-blue/10 p-4">
              <div className="flex items-start gap-3">
                <Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-ctp-blue" />
                <p className="text-xl leading-8 text-[#a0988c]">
                  Use these examples to quickly explore the transformation flow and test the system without uploading your own model.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              {examples.map((example) => (
                <button
                  type="button"
                  key={example.id}
                  onClick={() => handleSelect(example)}
                  className="group w-full rounded-3xl border border-ctp-surface1 bg-ctp-surface0/40 p-6 text-left transition-all duration-300 hover:border-ctp-mauve/50 hover:bg-ctp-surface0"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="text-3xl font-bold text-ctp-text">{example.name}</div>
                      <p className="mt-3 text-xl leading-8 text-[#a0988c]">
                        {example.description}
                      </p>
                    </div>
                    <ChevronRight className="mt-1 h-6 w-6 shrink-0 text-[#a0988c] transition-transform group-hover:translate-x-1 group-hover:text-ctp-text" />
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    {example.tags.map(([label, colors]) => (
                      <span
                        key={label}
                        className={`rounded-lg border px-3 py-1 text-base font-bold uppercase tracking-wide ${colors}`}
                      >
                        {label}
                      </span>
                    ))}
                  </div>

                  <div className="mt-4 overflow-hidden rounded-2xl border border-ctp-surface1 bg-white/95 p-2 shadow-inner shadow-black/5">
                    <img
                      src={example.previewImage}
                      alt={example.previewAlt}
                      className="h-auto w-full rounded-xl object-contain"
                    />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
