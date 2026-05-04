import Swal from "sweetalert2"

const popupClasses = {
  popup: "rounded-2xl border border-ctp-surface1 bg-ctp-mantle text-ctp-text shadow-2xl shadow-black/30",
  title: "text-2xl font-bold text-ctp-text",
  htmlContainer: "text-base text-[#a0988c]",
  confirmButton: "rounded-lg bg-ctp-red px-4 py-2 font-semibold text-ctp-base transition-colors hover:bg-[#f38ba8]",
  cancelButton: "rounded-lg border border-ctp-surface1 bg-ctp-surface0 px-4 py-2 font-semibold text-ctp-text transition-colors hover:bg-ctp-surface1",
  actions: "gap-3",
}

export const confirmClear = async ({ title, text }) => {
  const result = await Swal.fire({
    title,
    text,
    icon: "warning",
    iconColor: "#f38ba8",
    background: "#1e1e2e",
    color: "#cdd6f4",
    showCancelButton: true,
    confirmButtonText: "Clear",
    cancelButtonText: "Cancel",
    reverseButtons: true,
    focusCancel: true,
    buttonsStyling: false,
    customClass: popupClasses,
  })

  return result.isConfirmed
}
