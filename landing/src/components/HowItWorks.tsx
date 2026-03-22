import { motion } from "framer-motion";

const steps = [
  {
    number: "01",
    title: "Add your fragrances",
    description: "Type or search to build your personal perfume wardrobe in seconds.",
    icon: "🌿",
  },
  {
    number: "02",
    title: "Tell the bot your mood",
    description: "Feeling romantic, energized, or cozy? Just say the word.",
    icon: "💭",
  },
  {
    number: "03",
    title: "Get perfect suggestions",
    description: "Receive curated scent picks tailored to you — every single day.",
    icon: "💎",
  },
];

const HowItWorks = () => (
  <section id="how-it-works" className="py-24 lg:py-32 bg-secondary/50">
    <div className="container">
      <div className="text-center mb-16">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-sm font-medium text-primary mb-3"
        >
          Simple & intuitive
        </motion.p>
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.05 }}
          className="font-display text-3xl sm:text-4xl text-foreground"
        >
          How it works
        </motion.h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        {steps.map((step, i) => (
          <motion.div
            key={step.number}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.1 }}
            className="text-center"
          >
            <div className="w-16 h-16 rounded-2xl bg-card border border-border soft-shadow mx-auto mb-5 flex items-center justify-center text-2xl">
              {step.icon}
            </div>
            <span className="text-xs font-semibold text-primary/60 tracking-widest uppercase mb-2 block">
              Step {step.number}
            </span>
            <h3 className="font-semibold text-foreground mb-2">{step.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs mx-auto">
              {step.description}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

export default HowItWorks;
