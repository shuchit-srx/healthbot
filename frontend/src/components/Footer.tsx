export default function Footer() {
  return (
    <footer
      className="
        border-t
        px-4 py-6
        text-center
        text-xs
      "
      style={{
        borderColor: "var(--border)",
        color: "var(--muted-foreground)",
      }}
    >
      <p>
        HealthBot provides educational information
        and is not a substitute for professional
        medical advice.
      </p>

      <p className="mt-2">
        Always consult a qualified healthcare
        professional for diagnosis and treatment.
      </p>
    </footer>
  );
}