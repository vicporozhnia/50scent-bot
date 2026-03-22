import { motion } from "framer-motion";

const testimonials = [
  {
    quote: "I never realized how much joy organizing my perfumes could bring. Now I reach for the right scent every morning without overthinking.",
    name: "Anya",
    detail: "12 fragrances in wardrobe",
  },
  {
    quote: "The mood-based search is magic. I just type 'cozy evening' and it knows exactly what I need.",
    name: "Sofia",
    detail: "Daily user",
  },
  {
    quote: "Finally an app that treats perfumes the way they deserve — with elegance and care. Absolutely love it.",
    name: "Marie",
    detail: "8 fragrances in wardrobe",
  },
];

const TestimonialsSection = () => (
  <section className="py-24 lg:py-32 bg-secondary/50">
    <div className="container">
      <div className="text-center mb-16">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-sm font-medium text-primary mb-3"
        >
          Loved by scent lovers
        </motion.p>
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.05 }}
          className="font-display text-3xl sm:text-4xl text-foreground"
        >
          What our users say
        </motion.h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        {testimonials.map((t, i) => (
          <motion.div
            key={t.name}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.08 }}
            className="p-6 rounded-2xl bg-card border border-border soft-shadow"
          >
            <p className="text-sm text-foreground/80 leading-relaxed mb-5 italic">
              "{t.quote}"
            </p>
            <div>
              <p className="text-sm font-semibold text-foreground">{t.name}</p>
              <p className="text-xs text-muted-foreground">{t.detail}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

export default TestimonialsSection;
