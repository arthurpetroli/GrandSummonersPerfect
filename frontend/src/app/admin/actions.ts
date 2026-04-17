"use server";

import { revalidatePath } from "next/cache";

import {
  getAdminGsinfoUnitsStatus,
  postAdminPublish,
  postAdminRunSync,
  postAdminSyncGsinfoUnits,
  postAdminSourceImport,
  postAdminSyncImages,
} from "@/lib/api";

export async function runTierlistSheetImportAction(formData: FormData): Promise<void> {
  const spreadsheetUrl = String(
    formData.get("spreadsheet_url") ||
      "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit"
  );
  const gid = String(formData.get("gid") || "116729514");

  await postAdminSourceImport({
    source_id: "src_sheet_tier",
    entity_type: "tierlist_entry",
    spreadsheet_url: spreadsheetUrl,
    gid,
    dry_run: true,
  });
  revalidatePath("/admin");
}

export async function runTierlistSheetApplyAction(formData: FormData): Promise<void> {
  const spreadsheetUrl = String(
    formData.get("spreadsheet_url") ||
      "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit"
  );
  const gid = String(formData.get("gid") || "116729514");

  await postAdminSourceImport({
    source_id: "src_sheet_tier",
    entity_type: "tierlist_entry",
    spreadsheet_url: spreadsheetUrl,
    gid,
    dry_run: false,
  });
  revalidatePath("/admin");
}

export async function runAutoSyncAction(formData: FormData): Promise<void> {
  const force = String(formData.get("force") || "0") === "1";
  await postAdminRunSync({ force });
  revalidatePath("/admin");
}

export async function runImageSyncAction(): Promise<void> {
  await postAdminSyncImages();
  revalidatePath("/admin");
  revalidatePath("/units");
}

export async function runGsinfoUnitsSyncAction(): Promise<void> {
  await postAdminSyncGsinfoUnits();
  revalidatePath("/admin");
  revalidatePath("/units");
}

export async function refreshGsinfoStatusAction(): Promise<void> {
  await getAdminGsinfoUnitsStatus();
  revalidatePath("/admin");
}

export async function publishDraftAction(formData: FormData): Promise<void> {
  const draftId = String(formData.get("draft_id") || "").trim();
  if (!draftId) {
    return;
  }

  await postAdminPublish({
    entity_type: "tierlist_draft",
    entity_id: draftId,
    reviewer: "admin_ui",
    change_notes: ["Published via admin panel action"],
  });

  revalidatePath("/admin");
  revalidatePath("/tierlists");
}
