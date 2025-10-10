import fs from 'node:fs';
import path from 'node:path';
import { PrismaClient } from '@/generated/prisma';

function ensurePrismaEnginesConfigured() {
  const enginesDir = path.join(process.cwd(), 'node_modules', '@prisma', 'engines');
  const queryEngine = path.join(enginesDir, 'libquery_engine-debian-openssl-1.1.x.so.node');
  const schemaEngine = path.join(enginesDir, 'schema-engine-debian-openssl-1.1.x');

  if (!process.env.PRISMA_QUERY_ENGINE_LIBRARY && fs.existsSync(queryEngine)) {
    process.env.PRISMA_QUERY_ENGINE_LIBRARY = queryEngine;
  }

  if (!process.env.PRISMA_SCHEMA_ENGINE_BINARY && fs.existsSync(schemaEngine)) {
    process.env.PRISMA_SCHEMA_ENGINE_BINARY = schemaEngine;
  }

  if (!process.env.PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING) {
    process.env.PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING = '1';
  }
}

function ensureDatabaseUrlAbsolute() {
  const rawUrl = process.env.DATABASE_URL;
  if (!rawUrl?.startsWith('file:')) {
    return;
  }

  const [, filePath = ''] = rawUrl.split('file:');
  if (!filePath) {
    return;
  }

  const isAbsolute = path.isAbsolute(filePath);
  if (isAbsolute) {
    return;
  }

  const absolutePath = path.resolve(process.cwd(), filePath);
  process.env.DATABASE_URL = `file:${absolutePath}`;
}

ensurePrismaEnginesConfigured();
ensureDatabaseUrlAbsolute();

declare global {
  var prisma: PrismaClient | undefined;
}

const prisma = globalThis.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== 'production') {
  globalThis.prisma = prisma;
}

export default prisma;
