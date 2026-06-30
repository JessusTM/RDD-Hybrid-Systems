import {sendAnswers} from "../../../services/questions";
import { useState } from "react";
/**
 * Guided questions modal used by the AI-assisted CIM-to-PIM interaction flow.
 */

/**
 * Displays the prepared questions generated after the CIM-to-PIM step.
 *
 * This component is used by the main application when guided interaction is available so
 * the user can review the generated questions in a dedicated modal view.
 */
const GuidedQuestionsModal = ({ isOpen, onClose, questions, onContinue, uvlPath }) => {
  const [answers, setAnswers] = useState({});

  const handleSelect = (questionId, option) => {
    setAnswers((prev) => ({ ...prev, [questionId]: option }));
  }

  const handleSubmit = async () => {
    try {
      const result = await sendAnswers(uvlPath, answers);
      console.log("Respuestas guardadas:", result);
      onContinue(result);

    } catch (error) {
      console.error("Error submitting answers:", error);
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-xl relative">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-2 right-2 text-white hover:text-blue-400 mr-3 mt-3"
        >
          X
        </button>

        <div className="flex items-center mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-6 h-6 text-purple-400 mr-2"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M7 17h3l2-4V7H7v6h2l-2 4zm7 0h3l2-4V7h-5v6h2l-2 4z" />
          </svg>

          <h2 className="text-xl font-bold text-white">Guided Interaction: CIM to PIM</h2>
        </div>

        <div className="bg-gray-900 p-4 mb-4 -mx-6 max-h-[420px] overflow-y-auto">
          <p className="text-gray-300">
            Review the questions generated to inspect the semi-automatic transformation from <span className="font-bold text-blue-200">CIM to PIM</span>
          </p>

          {questions.length === 0 ? (
            <div className="mt-6 rounded-lg border border-dashed border-gray-600 bg-gray-800/60 p-4">
              <p className="text-sm text-gray-300">
                No guided questions were generated for this UVL analysis.
              </p>
            </div>
          ) : (
            questions.map((q, index) => (
              <div key={q.id || index} className="mt-6 bg-gray-700 p-4 rounded-lg">
                <h3 className="text-white font-semibold mb-2">{q.text}</h3>
                <div className="flex flex-wrap gap-2 mt-3">
                  {q.options?.map((opt, optionIndex) => (
                    <button
                      type="button"
                      key={optionIndex}
                      onClick={() => handleSelect(q.id, opt)}
                      className={`px-3 py-2 rounded
                        ${
                          answers[q.id] === opt
                            ? "bg-blue-600 text-white"
                            : "bg-gray-600 text-gray-300 hover:bg-gray-500"
                        }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleSubmit}
            className="bg-gray-700 text-white px-4 py-2 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default GuidedQuestionsModal
