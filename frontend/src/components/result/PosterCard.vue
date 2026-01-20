<template>
  <div class="poster-container" id="poster-capture-area">
    <div class="poster-canvas">
      <!-- Header Section -->
      <header class="poster-header">
        <div class="pill-badge">{{ data.subtitle }}</div>
        <h1 class="poster-title">{{ data.title }}</h1>
      </header>

      <!-- Main Content -->
      <main class="poster-content">
        <!-- Optional Central Illustration/Symbol -->
        <div class="center-symbol" v-if="data.sections.length > 0">
          <div class="glow-circle">?</div>
          <div class="hand-drawn-arrows">
            <svg width="200" height="100" viewBox="0 0 200 100" fill="none">
              <path d="M70 20 L30 60" stroke="#ccc" stroke-width="2" stroke-linecap="round" marker-end="url(#arrowhead)" />
              <path d="M130 20 L170 60" stroke="#ccc" stroke-width="2" stroke-linecap="round" marker-end="url(#arrowhead)" />
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#ccc" />
                </marker>
              </defs>
            </svg>
          </div>
        </div>

        <!-- Sections Grid -->
        <div class="sections-grid">
          <div 
            v-for="(section, index) in data.sections" 
            :key="index" 
            class="section-card"
            :class="section.style"
          >
            <div class="section-icon">{{ mapIcon(section.icon) }}</div>
            <h3 class="section-heading">{{ section.heading }}</h3>
            <div class="section-divider"></div>
            <div class="section-body">
              <template v-if="Array.isArray(section.content)">
                <p v-for="(item, i) in section.content" :key="i">• {{ item }}</p>
              </template>
              <p v-else>{{ section.content }}</p>
            </div>
          </div>
        </div>

        <!-- Gold Quote -->
        <div v-if="data.quote" class="quote-box">
          <div class="quote-mark">“</div>
          <p class="quote-text">{{ data.quote }}</p>
        </div>
      </main>

      <!-- Footer -->
      <footer class="poster-footer">
        <div class="footer-line"></div>
        <div class="footer-content">
          <p class="summary-text">{{ data.summary || '效率控必看 · 一张图讲清楚' }}</p>
          <div class="brand">
            <span class="logo">RedInk AI</span>
            <span class="copyright">© 2026</span>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PosterData } from '../../stores/generator'

defineProps<{
  data: PosterData
}>()

const mapIcon = (icon: string) => {
  const mapping: Record<string, string> = {
    '[LIGHTBULB]': '💡',
    '[CHECK]': '✅',
    '[CROSS]': '❌',
    '[STAR]': '⭐',
    '[ARROW]': '➡',
    '[BOT]': '🤖',
    '[MANUAL]': '✍',
    '[LOOP]': '🔄',
    '[DOC]': '📄',
    '[TARGET]': '🎯',
    '[IDEA]': '💡',
    '[SUCCESS]': '🎉',
    '[QUESTION]': '❓'
  }
  return mapping[icon.toUpperCase()] || icon
}
</script>

<style scoped>
.poster-container {
  display: flex;
  justify-content: center;
  padding: 40px;
  background: #f0f0f0;
  min-height: 100vh;
}

.poster-canvas {
  width: 600px;
  background-color: #fcfaf2; /* Off-white / Cream */
  padding: 60px 50px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #333;
}

.poster-header {
  text-align: center;
  margin-bottom: 40px;
}

.pill-badge {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

.poster-title {
  font-size: 42px;
  font-weight: 800;
  line-height: 1.2;
  margin: 0;
  color: #1a1a1a;
}

.poster-content {
  flex: 1;
}

.center-symbol {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: -20px;
}

.glow-circle {
  width: 80px;
  height: 80px;
  background: #fff9c4;
  border: 2px solid #fdd835;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 800;
  color: #333;
  z-index: 2;
  box-shadow: 0 0 20px rgba(253, 216, 53, 0.4);
}

.hand-drawn-arrows {
  margin-top: -10px;
  z-index: 1;
}

.sections-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 20px;
}

.section-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.2s;
}

.section-card.positive { border-bottom: 4px solid #4caf50; }
.section-card.negative { border-bottom: 4px solid #f44336; }
.section-card.neutral { border-bottom: 4px solid #2196f3; }

.section-icon {
  font-size: 28px;
  margin-bottom: 12px;
}

.section-heading {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.section-divider {
  width: 30px;
  height: 2px;
  background: #eee;
  margin-bottom: 12px;
}

.section-body {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
}

.section-body p {
  margin: 4px 0;
}

.quote-box {
  margin-top: 40px;
  background: #fffef0;
  border-left: 4px solid #ffd54f;
  padding: 20px 30px;
  position: relative;
}

.quote-mark {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 48px;
  color: #ffd54f;
  line-height: 1;
  opacity: 0.3;
}

.quote-text {
  font-size: 18px;
  font-style: italic;
  font-weight: 600;
  color: #444;
  margin: 0;
}

.poster-footer {
  margin-top: 60px;
}

.footer-line {
  height: 1px;
  background: #eee;
  margin-bottom: 20px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.summary-text {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

.brand {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.logo {
  font-weight: 900;
  font-size: 14px;
  color: #1a1a1a;
}

.copyright {
  font-size: 10px;
  color: #999;
}
</style>
