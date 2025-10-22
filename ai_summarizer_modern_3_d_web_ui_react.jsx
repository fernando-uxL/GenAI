import React, { useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html, Environment, Float } from "@react-three/drei";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";

// === 3D Scene Components ===
function WobblyBlob() {
  const mesh = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (mesh.current) {
      mesh.current.rotation.x = Math.sin(t / 2) * 0.2;
      mesh.current.rotation.y = Math.cos(t / 3) * 0.25;
    }
  });
  return (
    <Float speed={1.5} rotationIntensity={0.6} floatIntensity={0.8}>
      <mesh ref={mesh} scale={[1.6, 1.6, 1.6]}>
        <icosahedronGeometry args={[1.1, 5]} />
        <meshPhysicalMaterial
          metalness={0.3}
          roughness={0.2}
          transmission={0.9}
          thickness={1.2}
          ior={1.2}
          color="#7aa2ff"
          clearcoat={1}
          clearcoatRoughness={0.1}
        />
      </mesh>
    </Float>
  );
}

function AnimatedRings() {
  const group = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (group.current) group.current.rotation.z = t / 12;
  });
  return (
    <group ref={group}>
      {[...Array(6)].map((_, i) => (
        <mesh key={i} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[2 + i * 0.35, 0.015 + i * 0.003, 128, 256]} />
          <meshStandardMaterial color="#bcd2ff" emissive="#183063" emissiveIntensity={0.15} />
        </mesh>
      ))}
    </group>
  );
}

// === UI Component ===
export default function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");

  const onFileChange = (e) => {
    setFile(e.target.files?.[0] || null);
    setSummary("");
    setError("");
  };

  const upload = async () => {
    if (!file) return;
    setLoading(true);
    setProgress(10);
    setSummary("");
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: form,
      });

      setProgress(70);

      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();
      setProgress(100);
      setSummary(data.summary || "No summary returned.");
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const copy = async () => {
    if (!summary) return;
    try {
      await navigator.clipboard.writeText(summary);
    } catch {}
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[radial-gradient(ellipse_at_top,rgba(26,38,77,0.7),#060914)] text-white">
      {/* 3D Canvas Background */}
      <div className="absolute inset-0 -z-10">
        <Canvas camera={{ position: [0, 0, 6], fov: 60 }}>
          <ambientLight intensity={0.6} />
          <directionalLight position={[4, 6, 5]} intensity={1.1} />
          <Environment preset="city" />
          <WobblyBlob />
          <AnimatedRings />
          <OrbitControls enableZoom={false} enablePan={false} />
        </Canvas>
      </div>

      {/* Glass overlay grid */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[url('https://transparenttextures.com/patterns/pw-maze-white.png')] opacity-10" />

      {/* Header */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-2xl font-semibold tracking-tight text-white/90"
        >
          AI Summarizer <span className="text-white/60">· Gemini</span>
        </motion.h1>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <a
            href="#"
            className="rounded-xl bg-white/10 px-4 py-2 text-sm backdrop-blur-md ring-1 ring-inset ring-white/20 hover:bg-white/15"
          >
            Docs
          </a>
        </motion.div>
      </header>

      {/* Main Card */}
      <main className="mx-auto grid max-w-5xl grid-cols-1 gap-6 px-6 pb-16 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="border-white/10 bg-white/10 text-white backdrop-blur-2xl">
            <CardHeader>
              <CardTitle>Upload a PDF / TXT</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-2xl border border-white/15 bg-white/5 p-4">
                <label className="mb-2 block text-sm text-white/80">Choose file</label>
                <Input type="file" accept=".pdf,.txt" onChange={onFileChange} className="cursor-pointer" />
                {file && (
                  <p className="mt-2 truncate text-xs text-white/70">Selected: {file.name}</p>
                )}
              </div>

              <div className="flex items-center gap-3">
                <Button onClick={upload} disabled={!file || loading} className="rounded-xl">
                  {loading ? "Summarizing…" : "Summarize with Gemini"}
                </Button>
                {progress > 0 && (
                  <div className="w-full">
                    <Progress value={progress} className="h-2 bg-white/10" />
                  </div>
                )}
              </div>

              {error && (
                <p className="text-sm text-rose-300">{error}</p>
              )}

              <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-xs text-white/70">
                Make sure your FastAPI server is running on <code>http://127.0.0.1:8000</code> and CORS is enabled.
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="border-white/10 bg-white/10 text-white backdrop-blur-2xl">
            <CardHeader>
              <CardTitle>Result</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                readOnly
                value={summary}
                placeholder="Your JSON summary will appear here…"
                className="min-h-[340px] resize-none border-white/10 bg-black/30 text-white/90 placeholder:text-white/40"
              />
              <div className="mt-4 flex items-center justify-end gap-3">
                <Button variant="secondary" onClick={copy} disabled={!summary} className="rounded-xl">
                  Copy JSON
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="mx-auto max-w-6xl px-6 pb-8 text-center text-xs text-white/50">
        Built with React, @react-three/fiber, drei, Tailwind, framer-motion, and shadcn/ui.
      </footer>
    </div>
  );
}
